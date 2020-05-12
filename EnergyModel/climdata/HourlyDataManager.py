from pyllist import dllist, dllistnode

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
    def __get_manager():
        """ Static access method. """
        if HourlyDataManager.__hourly_data_list is None:
            HourlyDataManager()
        return HourlyDataManager.__hourly_data_list

    def search_for_hourly_data(city, clg_sp, htg_sp):
        list = HourlyDataManager.__get_manager()
        for x in list.iternodes():
            if(x.value.equals_hourly_data(city, clg_sp, htg_sp)):
                return x.value.dataframe
        return None

    def add_hourly_data(hourly_data):
        if (not(isinstance(hourly_data, HourlyData))):
            raise TypeError("Tried to add non-hourly data object to hourly data manager")
        list = HourlyDataManager.__get_manager()
        list.appendright(hourly_data)

class HourlyData():
    def __init__(self, dataframe, city, clg_balance_point, htg_balance_point):
        self.city = city
        self.clg_balance_point = clg_balance_point
        self.htg_balance_point = htg_balance_point
        self.dataframe = dataframe

    def equals_hourly_data(self, city, clg_balance_point, htg_balance_point):
        if (self.clg_balance_point != clg_balance_point or 
            self.htg_balance_point != htg_balance_point or 
            self.city != city):
            return False
        return True