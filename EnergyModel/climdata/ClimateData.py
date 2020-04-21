from haversine import haversine, Unit
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

class ClimateData(object):
    """Hold all necessary climate information for energy calculations"""
    def __init__(self):
        self.clg_swing_temp = 60
        self.htg_swing_temp = 56
        self.clg_design_temp = 95
        self.htg_design_temp = 12
        self.cdd = 0
        self.hdd = 0
        self.eflh_c = 0
        self.eflh_h = 0
        self.eflh_t = 0
        self.clg_hrs = 0
        self.htg_hrs = 0
        self.avg_clg_load_pct = 0
        self.avg_htg_load_pct = 0
        self.closest_climate_zone = None

    def get_closest_climate_zone(self, lat, lon):
        #check that lat/lon are good
        if (lat == 0 or lon == 0):
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

    def calculate_climate_data(self):
        dataframe = self.__open_hourly_data()
        self.__append_cdd(dataframe)
        self.__append_hdd(dataframe)
        self.__append_eflh_c(dataframe)
        self.__append_eflh_h(dataframe)
        self.__append_eflh_t(dataframe)
        self.__append_clg_hrs(dataframe)
        self.__append_htg_hrs(dataframe)

    def __open_hourly_data(self):
        # check that climate zone is populated
        if (self.closest_climate_zone == None):
            raise TypeError("No climate zone to check weather data")
        data = pd.read_csv('reference/' + str(self.closest_climate_zone) + '.csv')
        return data

    def __calc_hourly_cdd(self, temp, swing_temp):
        calc = temp - swing_temp
        if (calc < 0):
            return 0
        else:
            return calc/24

    def __calc_hourly_hdd(self, temp, swing_temp):
        calc = swing_temp - temp
        if (calc < 0):
            return 0
        else:
            return calc/24

    def __calc_hourly_eflh_c(self, cdd, design_temp, swing_temp):
        return cdd/(design_temp - swing_temp)

    def __calc_hourly_eflh_h(self, hdd, design_temp, swing_temp):
        return hdd/(swing_temp - design_temp)

    def __calc_clg_hr(self, temp, swing_temp):
        if (temp - swing_temp > 0):
            return 1
        return 0

    def __calc_htg_hr(self, temp, swing_temp):
        if (temp - swing_temp > 0):
            return 0
        return 1

    #add CDD hourly to dataframe
    def __append_cdd(self, dataframe):
        dataframe['CDD'] = dataframe.apply(lambda x: self.__calc_hourly_cdd(x['DRY BULB'], self.clg_swing_temp), axis = 1)
        print(dataframe)
        return dataframe

    #add HDD hourly to dataframe
    def __append_hdd(self, dataframe):
        dataframe['HDD'] = dataframe.apply(lambda x: self.__calc_hourly_hdd(x['DRY BULB'], self.htg_swing_temp), axis = 1)
        print(dataframe)
        return dataframe

    #add EFLH-C to dataframe
    def __append_eflh_c(self, dataframe):
        dataframe['EFLH-C'] = dataframe.apply(lambda x: self.__calc_hourly_eflh_c(x['CDD'], self.clg_design_temp, self.clg_swing_temp), axis = 1)
        print(dataframe)
        return dataframe

    #add EFLH-H to dataframe
    def __append_eflh_h(self, dataframe):
        dataframe['EFLH-H'] = dataframe.apply(lambda x: self.__calc_hourly_eflh_h(x['HDD'], self.htg_design_temp, self.htg_swing_temp), axis = 1)
        print(dataframe)
        return dataframe

    #add EFLH-T to dataframe
    def __append_eflh_t(self, dataframe):
        dataframe['EFLH-T'] = dataframe.apply(lambda x: x['EFLH-C'] + x['EFLH-H'], axis = 1)
        print(dataframe)
        return dataframe

    #add clg hrs to dataframe
    def __append_clg_hrs(self, dataframe):
        dataframe['CLG-HRS'] = dataframe.apply(lambda x: self.__calc_clg_hr(x['DRY BULB'], self.clg_swing_temp), axis = 1)
        print(dataframe)
        return dataframe

    #add htg hours to dataframe
    def __append_htg_hrs(self, dataframe):
        dataframe['HTG-HRS'] = dataframe.apply(lambda x: self.__calc_htg_hr(x['DRY BULB'], self.htg_swing_temp), axis = 1)
        print(dataframe)
        return dataframe

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
        print()
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXX CLIMATE DATA OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")