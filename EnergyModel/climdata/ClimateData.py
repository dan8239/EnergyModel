from haversine import haversine, Unit
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile
from utility import Assumptions
from climdata import HourlyDataManager, HourlyDataProcessor

class ClimateData():
    """Hold all necessary climate information for energy calculations"""
    def __init__(self, 
                 type = "Occupied"):
        if (type == "Occupied"):
            self.clg_balance_point_temp = Assumptions.ClimateDefaults.occ_clg_balance_point_temp
            self.htg_balance_point_temp = Assumptions.ClimateDefaults.occ_htg_balance_point_temp
        else:
            self.clg_balance_point_temp = Assumptions.ClimateDefaults.unocc_clg_balance_point_temp
            self.htg_balance_point_temp = Assumptions.ClimateDefaults.unocc_htg_balance_point_temp
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
        self.avg_clg_fan_speed_pct_from_speed = 0
        self.avg_htg_fan_speed_pct_from_speed = 0
        self.avg_clg_fan_speed_pct_from_power = 0
        self.avg_htg_fan_speed_pct_from_power = 0
        self.closest_climate_city = None
        self.climate_zone = None
        self.type = "Occupied"

    def get_closest_climate_city(self, lat, lon):
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
                climate_zone = data['CLIMATE ZONE CODE'][i]
        self.climate_zone = climate_zone
        self.closest_climate_city = closest_city
        self.clg_design_temp = clg_design_tmp
        self.htg_design_temp = htg_design_tmp
        return closest_city, clg_design_tmp, htg_design_tmp

    def copy_climate_data(self, climate_data_to_copy):
        self.clg_balance_point_temp = climate_data_to_copy.clg_balance_point_temp
        self.htg_balance_point_temp = climate_data_to_copy.htg_balance_point_temp
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
        self.avg_clg_fan_speed_pct_from_speed = climate_data_to_copy.avg_clg_fan_speed_pct_from_speed
        self.avg_htg_fan_speed_pct_from_speed = climate_data_to_copy.avg_htg_fan_speed_pct_from_speed
        self.avg_clg_fan_speed_pct_from_power = climate_data_to_copy.avg_clg_fan_speed_pct_from_power
        self.avg_htg_fan_speed_pct_from_power = climate_data_to_copy.avg_htg_fan_speed_pct_from_power
        self.closest_climate_city = climate_data_to_copy.closest_climate_city
        self.climate_zone = climate_data_to_copy.climate_zone

    def update_climate_data(self, htg_balance_point_temp, clg_balance_point_temp):
        print("Updating Climate Data for " + str(self.closest_climate_city))
        if (self.closest_climate_city == None):
            raise TypeError("Climate Zone Updated before being instantiated")
        self.htg_balance_point_temp = htg_balance_point_temp
        self.clg_balance_point_temp = clg_balance_point_temp
        self.calculate_climate_data()



    def calculate_climate_data(self):
        print("Calculating Climate Data for " + str(self.closest_climate_city))
        dataframe = self.__get_hourly_data()
        
        self.cdd = dataframe['CDD'].sum()
        self.hdd = dataframe['HDD'].sum()
        self.eflh_c = dataframe['EFLH-C'].sum()
        self.eflh_h = dataframe['EFLH-H'].sum()
        self.eflh_t = dataframe['EFLH-T'].sum()
        self.clg_hrs = dataframe['CLG-HRS'].sum()
        self.htg_hrs = dataframe['HTG-HRS'].sum()
        if (self.clg_hrs != 0):
            self.avg_clg_load_pct = self.eflh_c/self.clg_hrs
            self.avg_clg_fan_speed_pct_from_speed = self.avg_clg_load_pct
            #roll up power, convert back to speed %
            self.avg_clg_fan_speed_pct_from_power = (dataframe['CLG-FAN-PWR-%'].sum()/self.clg_hrs)**(1.0/3.0)
        else:
            self.avg_clg_load_pct = 0
            self.avg_clg_fan_power_pct = 0
        if (self.htg_hrs != 0):
            self.avg_htg_load_pct = self.eflh_h/self.htg_hrs
            self.avg_htg_fan_speed_pct_from_speed = self.avg_htg_load_pct
            self.avg_htg_fan_speed_pct_from_power = (dataframe['HTG-FAN-PWR-%'].sum()/self.htg_hrs)**(1.0/3.0)
        else:
            self.avg_htg_load_pct = 0
        self.avg_clg_oa_t = self.avg_clg_load_pct*(self.clg_design_temp - self.clg_balance_point_temp) + self.clg_balance_point_temp
        self.avg_htg_oa_t = self.htg_balance_point_temp - self.avg_htg_load_pct*(self.htg_balance_point_temp - self.htg_design_temp)
        

#-----------------------------PRIVATE METHODS-------------------------------#

    def __get_hourly_data(self):
        hourly_data = HourlyDataManager.HourlyDataManager.search_for_hourly_data(self.closest_climate_city, 
                                                                                 self.clg_balance_point_temp, 
                                                                                 self.htg_balance_point_temp)
        #if no hit, open file and append, add to hourly data manager
        if (hourly_data is None):
            #open file
            hourly_data = self.__open_hourly_data()
            #add DOW if not existing
            hourly_data, data_updated = HourlyDataProcessor.add_dow(hourly_data)
            #save if changes were made
            if (data_updated):
                self.__save_hourly_data(hourly_data)
            #add needed columns to dataframe then add to hourly data manager
            hourly_data = HourlyDataProcessor.append_hourly_calcs(hourly_data, 
                                                                  self.clg_balance_point_temp, 
                                                                  self.htg_balance_point_temp, 
                                                                  self.clg_design_temp, 
                                                                  self.htg_design_temp)
            HourlyDataManager.HourlyDataManager.add_hourly_data(HourlyDataManager.HourlyData(hourly_data,
                                                                                             self.closest_climate_city,
                                                                                             self.clg_balance_point_temp,
                                                                                             self.htg_balance_point_temp))
        return hourly_data

    def __open_hourly_data(self):
        # check that climate zone is populated
        if (self.closest_climate_city == None):
            raise TypeError("No climate zone to check weather data")
        dataframe = pd.read_csv('reference/' + str(self.closest_climate_city) + '.csv')
        return dataframe
    
    def __save_hourly_data(self, dataframe):
        print("Updating Hourly Temperature File")
        dataframe.to_csv('reference/' + str(self.closest_climate_city) + '.csv')

    

