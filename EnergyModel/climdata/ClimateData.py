from haversine import haversine, Unit
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile

class ClimateData():
    """Hold all necessary climate information for energy calculations"""
    def __init__(self):
        self.clg_swing_temp = 60
        self.htg_swing_temp = 56
        self.clg_design_temp = 0
        self.htg_design_temp = 0
        self.cdd = 0
        self.hdd = 0
        self.eflh_c = 0
        self.eflh_h = 0
        self.eflh_t = 0
        self.clg_hrs = 0
        self.htg_hrs = 0
        self.avg_clg_load_pct = 0
        self.avg_htg_load_pct = 0
        self.avg_clg_oa_t = 0
        self.avg_htg_oa_t = 0
        self.closest_climate_zone = None

    def get_closest_climate_zone(self, lat, lon):
        #check that lat/lon are good
        if (lat == 0 or lon == 0 or lat == np.nan or lon == np.nan):
            raise TypeError("Lat or Lon of 0 input to find closest weather data")

        #temp variables to check closest city
        input_city = (lat, lon)
        min_distance = float(99999999)
        temp_distance = float(99999999)
        closest_city = "No result"

        #create data frame from csv
        data = pd.read_csv('reference/CLIMATE-ZONE-LIST.csv')
        for i in data.index:
            
            temp_city = (pd.to_numeric(data['LAT'][i]), pd.to_numeric(data['LON'][i]))
            temp_distance = haversine(input_city, temp_city, unit=Unit.MILES)
            if (temp_distance < min_distance):
                min_distance = temp_distance
                closest_city = data['CLIMATE ZONE'][i]
                clg_design_tmp = data['DB DSGN TEMP C'][i]
                htg_design_tmp = data['DB DSGN TEMP H'][i]
        self.closest_climate_zone = closest_city
        self.clg_design_temp = clg_design_tmp
        self.htg_design_temp = htg_design_tmp
        return closest_city, clg_design_tmp, htg_design_tmp

    def copy_climate_data(self, climate_data_to_copy):
        self.clg_swing_temp = climate_data_to_copy.clg_swing_temp
        self.htg_swing_temp = climate_data_to_copy.htg_swing_temp
        self.clg_design_temp = climate_data_to_copy.clg_design_temp
        self.htg_design_temp = climate_data_to_copy.htg_design_temp
        self.cdd = climate_data_to_copy.cdd
        self.hdd = climate_data_to_copy.hdd
        self.eflh_c = climate_data_to_copy.eflh_c
        self.eflh_h = climate_data_to_copy.eflh_h
        self.eflh_t = climate_data_to_copy.eflh_t
        self.clg_hrs = climate_data_to_copy.clg_hrs
        self.htg_hrs = climate_data_to_copy.htg_hrs
        self.avg_clg_load_pct = climate_data_to_copy.avg_clg_load_pct
        self.avg_htg_load_pct = climate_data_to_copy.avg_htg_load_pct
        self.avg_clg_oa_t = climate_data_to_copy.avg_clg_oa_t
        self.avg_htg_oa_t = climate_data_to_copy.avg_htg_oa_t
        self.closest_climate_zone = climate_data_to_copy.closest_climate_zone

    def update_climate_data(self, htg_swing_temp, clg_swing_temp):
        if (self.closest_climate_zone == None or self.clg_design_temp == 0 or self.htg_design_temp == 0):
            raise TypeError("Climate Zone Updated before being instantiated")
        self.htg_swing_temp = htg_swing_temp
        self.clg_swing_temp = clg_swing_temp
        self.calculate_climate_data()

    def calculate_climate_data(self):
        dataframe = self.__open_hourly_data()
        print("Appending Cooling Degree Days")
        dataframe['CDD'] = self.__calc_hourly_cdd(dataframe['DRY BULB'].values, self.clg_swing_temp)
        print("Appending Heating Degree Days")
        dataframe['HDD'] = self.__calc_hourly_hdd(dataframe['DRY BULB'].values, self.htg_swing_temp)
        print("Appending EFLH Cooling")
        dataframe['EFLH-C'] = self.__calc_hourly_eflh_c(dataframe['CDD'].values, self.clg_design_temp, self.clg_swing_temp)
        print("Appending EFLH Heating")
        dataframe['EFLH-H'] = self.__calc_hourly_eflh_h(dataframe['HDD'].values, self.htg_design_temp, self.htg_swing_temp)
        print("Appending EFLH Total")
        dataframe['EFLH-T'] = self.__calc_hourly_eflh_t(dataframe['EFLH-C'].values, dataframe['EFLH-H'].values)
        print("Appending Cooling Hours")
        dataframe['CLG-HRS'] = self.__calc_clg_hr(dataframe['DRY BULB'].values, self.clg_swing_temp)
        print("Appending Heating Hours")
        dataframe['HTG-HRS'] = self.__calc_htg_hr(dataframe['DRY BULB'].values, self.htg_swing_temp)
        self.cdd = dataframe['CDD'].sum()
        self.hdd = dataframe['HDD'].sum()
        self.eflh_c = dataframe['EFLH-C'].sum()
        self.eflh_h = dataframe['EFLH-H'].sum()
        self.eflh_t = dataframe['EFLH-T'].sum()
        self.clg_hrs = dataframe['CLG-HRS'].sum()
        self.htg_hrs = dataframe['HTG-HRS'].sum()
        if (self.clg_hrs != 0):
            self.avg_clg_load_pct = self.eflh_c/self.clg_hrs
        else:
            self.avg_clg_load_pct = 0
        if (self.htg_hrs != 0):
            self.avg_htg_load_pct = self.eflh_h/self.htg_hrs
        else:
            self.avg_htg_load_pct = 0
        self.avg_clg_oa_t = self.avg_clg_load_pct*(self.clg_design_temp - self.clg_swing_temp) + self.clg_swing_temp
        self.avg_htg_oa_t = self.htg_swing_temp - self.avg_htg_load_pct*(self.htg_swing_temp - self.htg_design_temp)

    def __open_hourly_data(self):
        # check that climate zone is populated
        if (self.closest_climate_zone == None):
            raise TypeError("No climate zone to check weather data")
        data = pd.read_csv('reference/' + str(self.closest_climate_zone) + '.csv')
        return data

    def __calc_hourly_cdd(self, temp, swing_temp):
        calc = temp - swing_temp
        sign = (calc > 0)*1
        val = calc * sign / 24
        return val

    def __calc_hourly_hdd(self, temp, swing_temp):
        calc = swing_temp - temp
        sign = (calc > 0)*1
        val = calc * sign / 24
        return val

    def __calc_hourly_eflh_c(self, cdd, design_temp, swing_temp):
        return cdd*24/(design_temp - swing_temp)

    def __calc_hourly_eflh_h(self, hdd, design_temp, swing_temp):
        return hdd*24/(swing_temp - design_temp)

    def __calc_hourly_eflh_t(self, eflh_c, eflh_h):
        return eflh_c + eflh_h

    def __calc_clg_hr(self, temp, swing_temp):
        calc = ((temp - swing_temp) > 0)
        #convert to int
        return calc*1

    def __calc_htg_hr(self, temp, swing_temp):
        calc = ((swing_temp - temp) > 0)
        #convert to int
        return calc*1

    

    def dump(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print()
        print("Climate Zone: " + str(self.closest_climate_zone))
        print("Cooling Design Temp: " + str(self.clg_design_temp))
        print("Heating Design Temp: " + str(self.htg_design_temp))
        print("Cooling Swing Temp: " + str(self.clg_swing_temp))
        print("Heating Swing Temp: " + str(self.htg_swing_temp))
        print("Cooling Degree Days: " + str(self.cdd))
        print("Heating Degree Days: " + str(self.hdd))
        print("EFLH Cooling: " + str(self.eflh_c))
        print("EFLH Heating: " + str(self.eflh_h))
        print("EFLH Total: " + str(self.eflh_t))
        print("Cooling Hours: " + str(self.clg_hrs))
        print("Heating Hours: " + str(self.htg_hrs))
        print("Average Cooling Load Percentage: " + str(self.avg_clg_load_pct))
        print("Average Heating Load Percentage: " + str(self.avg_htg_load_pct))
        print("Average Cooling OA Temp: " + str(self.avg_clg_oa_t))
        print("Average Heating OA Temp: " + str(self.avg_htg_oa_t))
        print()
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX END OF CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")