from pyllist import dllist, dllistnode
from climdata import HourlyDataProcessor, LoadProfile
import pandas as pd

#singleton class. Just have search and add for hourly objects
class HourlyDataManager:
    __hourly_data_list = None
    """description of class"""
    def __init__(self):
        if (self.__hourly_data_list != None):
            raise Exception("Hourly Data Manager Is a Singleton!")
        else:
            HourlyDataManager.__hourly_data_list = dllist()

    @staticmethod
    #get instance of the list (singleton)
    def __get_manager():
        """ Static access method. """
        if HourlyDataManager.__hourly_data_list is None:
            HourlyDataManager()
        return HourlyDataManager.__hourly_data_list

    #Search for hourly data already existing on list
    @staticmethod
    def __search_for_hourly_data(city, 
                                 occ_clg_balance_temp,
                                 occ_htg_balance_temp,
                                 unocc_clg_balance_temp,
                                 unocc_htg_balance_temp):
        list = HourlyDataManager.__get_manager()
        for x in list.iternodes():
            if(x.value.equals_hourly_data(city, 
                                          occ_clg_balance_temp, 
                                          occ_htg_balance_temp,
                                          unocc_clg_balance_temp,
                                          unocc_htg_balance_temp)):
                return x.value
        return None

    #add an hourly_data object to the hourly manager list
    @staticmethod
    def __add_hourly_data(hourly_data):
        if (not(isinstance(hourly_data, HourlyData))):
            raise TypeError("Tried to add non-hourly data object to hourly data manager")
        list = HourlyDataManager.__get_manager()
        list.appendright(hourly_data)

    # Return Hourly Data Object from asset information (create new if needed)
    @staticmethod
    def get_hourly_data(asset):
        #get closest city and design conditions from the asset
        closest_city = asset.proposal.site.closest_climate_city
        clg_design_temp = asset.proposal.site.clg_design_temp
        htg_design_temp = asset.proposal.site.htg_design_temp
        #search to see if the hourly object already exists
        hourly_data = HourlyDataManager.__search_for_hourly_data(closest_city, 
                                                                   asset.occ_clg_balance_point_temp, 
                                                                   asset.occ_htg_balance_point_temp,
                                                                   asset.unocc_clg_balance_point_temp,
                                                                   asset.unocc_htg_balance_point_temp)
        #if no hit, open file and append, add to hourly data manager
        if (hourly_data is None):
            #open file
            hourly_dataframe = HourlyDataManager.__open_hourly_dataframe(closest_city)
            #add DOW if not existing
            hourly_dataframe, data_updated = HourlyDataProcessor.add_dow(hourly_dataframe)
            #save if changes were made
            if (data_updated):
                HourlyDataManager.__save_hourly_dataframe(hourly_dataframe, closest_city)
            #add needed columns to dataframe then add to hourly data manager
            hourly_dataframe = HourlyDataProcessor.append_hourly_calcs(hourly_dataframe, 
                                                                  asset.occ_clg_balance_point_temp, 
                                                                  asset.occ_htg_balance_point_temp, 
                                                                  clg_design_temp, 
                                                                  htg_design_temp)
            hourly_data = HourlyData(hourly_dataframe, 
                                     closest_city,
                                     asset.occ_clg_balance_point_temp,
                                     asset.occ_htg_balance_point_temp,
                                     asset.unocc_clg_balance_point_temp,
                                     asset.unocc_htg_balance_point_temp,
                                     clg_design_temp,
                                     htg_design_temp)
            HourlyDataManager.__add_hourly_data(hourly_data)
        return hourly_data

    #open hourly data from file
    @staticmethod
    def __open_hourly_dataframe(closest_climate_city):
        # check that climate zone is populated
        if (closest_climate_city == None):
            raise TypeError("No climate zone to check weather data")
        dataframe = pd.read_csv('reference/' + str(closest_climate_city) + '.csv')
        return dataframe
    
    #save hourly data to file
    @staticmethod
    def __save_hourly_dataframe(dataframe, closest_climate_city):
        print("Updating Hourly Temperature File")
        dataframe.to_csv('reference/' + str(closest_climate_city) + '.csv')

    

#----------------------------- Data Types ----------------------------

class HourlyData():
    def __init__(self, 
                 dataframe, 
                 city, 
                 occ_clg_balance_point, 
                 occ_htg_balance_point,
                 unocc_clg_balance_point, 
                 unocc_htg_balance_point,
                 clg_design_temp,
                 htg_design_temp):
        self.city = city
        self.occ_clg_balance_point = occ_clg_balance_point
        self.occ_htg_balance_point = occ_htg_balance_point
        self.unocc_clg_balance_point = unocc_clg_balance_point
        self.unocc_htg_balance_point = unocc_htg_balance_point
        self.clg_design_temp = clg_design_temp
        self.htg_design_temp = htg_design_temp
        self.dataframe = dataframe
        self.occ_load_profile = self.generate_load_profile()
        self.unocc_load_profile = None

    #check if hourly data matches the input conditions
    def equals_hourly_data(self, 
                           city, 
                           occ_clg_balance_point, 
                           occ_htg_balance_point,
                           unocc_clg_balance_point, 
                           unocc_htg_balance_point):
        if (self.city != city or 
            self.occ_clg_balance_point != occ_clg_balance_point or 
            self.occ_htg_balance_point != occ_htg_balance_point or 
            self.unocc_clg_balance_point != unocc_clg_balance_point or
            self.unocc_htg_balance_point != unocc_htg_balance_point):
            return False
        return True
    
    #generate load profile from hourly data
    def generate_load_profile(self):
        load_profile = LoadProfile.LoadProfile()
        load_profile.calculate_load_profile(self)
        return load_profile

    