import copy
import datetime

class Asset:
    def __init__(self, proposal = None, make = None, model = None, serial = None, manufactured_year = None):
        self.proposal = proposal
        self.make = make
        self.model = model
        self.serial = serial        
        self.manufactured_year = manufactured_year
        if (self.manufactured_year != None):
            self.age = int(d.datetime.now().year) - self.manufactured_year
        else:
            self.age = None
        self.filtered_asset = None

    def filter_asset(self):
        if (self.filtered_asset == None):
            self.filtered_asset = copy.deepcopy(self)
        if (self.age != None):
            self.filtered_asset.age = self.age
        self.derived_filter_asset()

    def derived_filter_asset():
        pass

    def dump(self):
        print("Asset Type: " + type(self).__name__)
        print("Make: " + str(self.make))
        print("Model: " + str(self.model))
        print("Serial: " + str(self.serial))
        print("Year: " + str(self.manufactured_year))
        self.derived_dump()
        if (self.filtered_asset != None):
            print("Filtered Asset: ")
            self.filtered_asset.dump()

    def derived_dump(self):
        pass