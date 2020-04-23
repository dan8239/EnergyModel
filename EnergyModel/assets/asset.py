import copy
import datetime

class Asset:
    def __init__(self, proposal = None, make = None, model = None, serial = None, manufactured_year = None):
        self.proposal = proposal
        self.make = make
        self.model = model
        self.serial = serial        
        self.manufactured_year = manufactured_year
        self.run_hours_yearly = 8760
        self.status = None
        self.kwh_yearly = 0
        self.therms_yearly = 0
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
        self.kwh_yearly = 0
        self.therms_yearly = 0
        self._derived_copy_asset(asset_to_copy)

    def _derived_copy_asset(self, asset_to_copy):
        pass

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