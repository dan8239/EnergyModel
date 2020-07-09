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
    def __search_for_hourly_data(city, asset):
        list = HourlyDataManager.__get_manager()
        for x in list.iternodes():
            if(x.value.equals_hourly_data(city, asset)):
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
        #search to see if the hourly object already exists with asset conditions
        hourly_data = HourlyDataManager.__search_for_hourly_data(closest_city, 
                                                                 asset)
        #if no hit, open file and append, add to hourly data manager
        if (hourly_data is None):
            #open file
            hourly_dataframe = HourlyDataManager.__open_hourly_dataframe(closest_city)
            #add DOW if not existing
            hourly_dataframe, data_updated = HourlyDataProcessor.add_dow(hourly_dataframe)
            #save if changes were made
            if (data_updated):
                HourlyDataManager.__save_hourly_dataframe(hourly_dataframe, closest_city)
            #add occupancy column to dataframe
            hourly_dataframe = HourlyDataProcessor.append_occ(hourly_dataframe,
                                                              asset.weekday_start_hour,
                                                              asset.weekday_stop_hour,
                                                              asset.weekend_start_hour,
                                                              asset.weekend_stop_hour)

            #calculate load conditions for subset of OCCUPIED time
            occ_df = hourly_dataframe.copy().loc[hourly_dataframe['OCC'] == True, :]
            occ_df = HourlyDataProcessor.append_hourly_calcs(occ_df, 
                                                             asset.occ_clg_balance_point_temp, 
                                                             asset.occ_htg_balance_point_temp, 
                                                             clg_design_temp, 
                                                             htg_design_temp)

            #calculate load conditions for subset of UNOCCUPIED time
            unocc_df = hourly_dataframe.copy().loc[hourly_dataframe['OCC'] == False, :]
            unocc_df = HourlyDataProcessor.append_hourly_calcs(unocc_df, 
                                                             asset.unocc_clg_balance_point_temp, 
                                                             asset.unocc_htg_balance_point_temp, 
                                                             clg_design_temp, 
                                                             htg_design_temp)
            
            #add (concat) and sort Occ/Unocc dataframes back together
            hourly_dataframe = pd.concat([occ_df, unocc_df]).sort_index()

            hourly_data = HourlyData(hourly_dataframe, 
                                     closest_city,
                                     asset.occ_clg_balance_point_temp,
                                     asset.occ_htg_balance_point_temp,
                                     asset.unocc_clg_balance_point_temp,
                                     asset.unocc_htg_balance_point_temp,
                                     clg_design_temp,
                                     htg_design_temp,
                                     asset.weekday_start_hour,
                                     asset.weekday_stop_hour,
                                     asset.weekend_start_hour,
                                     asset.weekend_stop_hour)
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
                 htg_design_temp,
                 weekday_start_hour,
                 weekday_stop_hour,
                 weekend_start_hour,
                 weekend_stop_hour):
        self.city = city
        self.occ_clg_balance_point = occ_clg_balance_point
        self.occ_htg_balance_point = occ_htg_balance_point
        self.unocc_clg_balance_point = unocc_clg_balance_point
        self.unocc_htg_balance_point = unocc_htg_balance_point
        self.clg_design_temp = clg_design_temp
        self.htg_design_temp = htg_design_temp
        self.weekday_start_hour = weekday_start_hour
        self.weekday_stop_hour = weekday_stop_hour
        self.weekend_start_hour = weekend_start_hour
        self.weekend_stop_hour = weekend_stop_hour
        self.dataframe = dataframe
        self.occ_load_profile = None
        self.unocc_load_profile = None
        self.__generate_load_profiles()

    #check if hourly data matches the input conditions
    def equals_hourly_data(self, 
                           city, 
                           asset):
        if (self.city != city or 
            self.occ_clg_balance_point != asset.occ_clg_balance_point_temp or 
            self.occ_htg_balance_point != asset.occ_htg_balance_point_temp or 
            self.unocc_clg_balance_point != asset.unocc_clg_balance_point_temp or
            self.unocc_htg_balance_point != asset.unocc_htg_balance_point_temp or
            self.weekday_start_hour != asset.weekday_start_hour or
            self.weekday_stop_hour != asset.weekday_stop_hour or
            self.weekend_start_hour != asset.weekend_start_hour or
            self.weekend_stop_hour != asset.weekend_stop_hour):
            return False
        return True
    
    #generate load profiles from hourly data for use in Model Calcs
    def __generate_load_profiles(self):
        #generate occ load profile, attach to hourly data object
        occ_load_profile = LoadProfile.LoadProfile()
        occ_load_profile.calculate_load_profile(self, occ = True)
        self.occ_load_profile = occ_load_profile

        #generate occ load profile, attach to hourly data object
        unocc_load_profile = LoadProfile.LoadProfile()
        unocc_load_profile.calculate_load_profile(self, occ = False)
        self.unocc_load_profile = unocc_load_profile

    