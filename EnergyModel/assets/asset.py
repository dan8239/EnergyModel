import copy
import datetime
from climdata import ClimateData

class Asset:
    def __init__(self, proposal = None, make = None, model = None, serial = None, manufactured_year = None):
        self.proposal = proposal
        self.make = make
        self.model = model
        self.serial = serial        
        self.manufactured_year = manufactured_year
        self.run_hours_yearly = 8760
        self.status = None
        self.kwh_hvac_yearly = 0
        self.therms_hvac_yearly = 0
        self.climate_data = None
        self.calc_age()

    def set_proposal(self, proposal):
        self.proposal = proposal

    def set_make(self, make):
        self.make

    def copy_asset(self, asset_to_copy):
        self.make = asset_to_copy.make
        self.model = asset_to_copy.model
        self.serial = asset_to_copy.serial
        self.manufactured_year = asset_to_copy.manufactured_year
        self.age = asset_to_copy.age
        self.run_hours_yearly = asset_to_copy.run_hours_yearly
        self.kwh_hvac_yearly = 0
        self.therms_hvac_yearly = 0
        self._derived_copy_asset(asset_to_copy)

    def _derived_copy_asset(self, asset_to_copy):
        pass

    def copy_asset_from_row(self, row):
        if (self.status == "existing"):
            self.__copy_existing_asset_from_row(row)
        elif (self.status == "new"):
            self.__copy_new_asset_from_row(row)
        else:
            raise TypeError("Asset Status Not Set")

    def _derived_copy_existing_asset_from_row(self, row):
        #raise NotImplementedError("Derived copy new asset from row not implemented for type " + str(type(self)))
        pass

    def _derived_copy_new_asset_from_row(self, row):
        #raise NotImplementedError("Derived copy new asset from row not implemented for type " + str(type(self)))
        pass

    def __copy_existing_asset_from_row(self, row):
        self.manufactured_year = row.year
        self.calc_age()
        self._derived_copy_existing_asset_from_row(row)
        
    def __copy_new_asset_from_row(self, row):
        self.manufactured_year = datetime.datetime.now().year
        self.calc_age()
        self._derived_copy_new_asset_from_row(row)


    def calc_age(self):
        if (self.manufactured_year != None):
            self.age = int(datetime.datetime.now().year) - self.manufactured_year
        else:
            self.age = None

    def filter_asset(self):
        self._derived_filter_asset()

    def _derived_filter_asset(self):
        pass

    def run_energy_calculations(self, energy_model):
        energy_model.calculate(self)

    def update_climate_data(self, htg_balance_point_temp, clg_balance_point_temp):
        new_clim_data = ClimateData.ClimateData()
        new_clim_data.copy_climate_data(self.climate_data)
        new_clim_data.update_climate_data(htg_balance_point_temp, clg_balance_point_temp)
        self.climate_data = new_clim_data

    def dump(self):
        print("Asset Type: " + type(self).__name__)
        #print("Make: " + str(self.make))
        #print("Model: " + str(self.model))
        #print("Serial: " + str(self.serial))
        #print("Year: " + str(self.manufactured_year))
        print("Age: " + str(self.age))
        self._derived_dump()

    def _derived_dump(self):
        pass