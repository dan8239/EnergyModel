import pandas as pd
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile
from utility import Assumptions
from climdata import HourlyDataManager, HourlyDataProcessor

class LoadProfile():
    """Hold all necessary climate information for energy calculations"""
    def __init__(self):
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
        self.type = "Occupied"

    def copy_load_profile(self, load_profile_to_copy):
        self.clg_balance_point_temp = load_profile_to_copy.clg_balance_point_temp
        self.htg_balance_point_temp = load_profile_to_copy.htg_balance_point_temp
        self.clg_design_temp = load_profile_to_copy.clg_design_temp
        self.htg_design_temp = load_profile_to_copy.htg_design_temp
        self.cdd = load_profile_to_copy.cdd
        self.hdd = load_profile_to_copy.hdd
        self.eflh_c = load_profile_to_copy.eflh_c
        self.eflh_h = load_profile_to_copy.eflh_h
        self.eflh_t = load_profile_to_copy.eflh_t
        self.clg_hrs = load_profile_to_copy.clg_hrs
        self.htg_hrs = load_profile_to_copy.htg_hrs
        self.avg_clg_load_pct = load_profile_to_copy.avg_clg_load_pct
        self.avg_htg_load_pct = load_profile_to_copy.avg_htg_load_pct
        self.avg_clg_oa_t = load_profile_to_copy.avg_clg_oa_t
        self.avg_htg_oa_t = load_profile_to_copy.avg_htg_oa_t
        self.avg_clg_fan_speed_pct_from_speed = load_profile_to_copy.avg_clg_fan_speed_pct_from_speed
        self.avg_htg_fan_speed_pct_from_speed = load_profile_to_copy.avg_htg_fan_speed_pct_from_speed
        self.avg_clg_fan_speed_pct_from_power = load_profile_to_copy.avg_clg_fan_speed_pct_from_power
        self.avg_htg_fan_speed_pct_from_power = load_profile_to_copy.avg_htg_fan_speed_pct_from_power
    

    def update_load_profile(self, htg_balance_point_temp, clg_balance_point_temp):
        print("Updating Climate Data for " + str(self.closest_climate_city))
        if (self.closest_climate_city == None):
            raise TypeError("Climate Zone Updated before being instantiated")
        self.htg_balance_point_temp = htg_balance_point_temp
        self.clg_balance_point_temp = clg_balance_point_temp
        self.calculate_load_profile()



    def calculate_load_profile(self, hourly_data, occ):
        if (not isinstance(hourly_data, HourlyDataManager.HourlyData)):
            raise TypeError("Cannot create load profile from object that is not HourlyData")
        print("Calculating Load Profile Data for " + str(hourly_data.city))

        #grab dataframe from hourly data object
        dataframe = hourly_data.dataframe
        #filter out just the occ or unocc values depending on which load profile type you want
        if (occ):
            dataframe = dataframe[dataframe['OCC'] == True]
        else:
            dataframe = dataframe[dataframe['OCC'] == False]
        
        self.clg_design_temp = hourly_data.clg_design_temp
        self.htg_design_temp = hourly_data.htg_design_temp
        self.cdd = dataframe['CDD'].sum()
        self.hdd = dataframe['HDD'].sum()
        self.eflh_c = dataframe['EFLH-C'].sum()
        self.eflh_h = dataframe['EFLH-H'].sum()
        self.eflh_t = dataframe['EFLH-T'].sum()
        self.clg_hrs = dataframe['CLG-HRS'].sum()
        self.htg_hrs = dataframe['HTG-HRS'].sum()
        self.vent_hrs = dataframe['VENT-HRS'].sum()
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
        self.avg_clg_oa_t = self.avg_clg_load_pct*(hourly_data.clg_design_temp - hourly_data.occ_clg_balance_point) + hourly_data.occ_clg_balance_point
        self.avg_htg_oa_t = hourly_data.occ_htg_balance_point - self.avg_htg_load_pct*(hourly_data.occ_htg_balance_point - hourly_data.htg_design_temp)
        

#-----------------------------PRIVATE METHODS-------------------------------#

    