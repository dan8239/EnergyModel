import copy
import datetime

class Asset:
    def __init__(self, proposal = None, make = None, model = None, serial = None, manufactured_year = None):
        self.proposal = proposal
        self.make = make
        self.model = model
        self.serial = serial        
        self.manufactured_year = manufactured_year
        self.calc_age()

    def set_proposal(self, proposal):
        self.proposal = proposal

    def set_make(self, make):
        self.make

    def calc_age(self):
        if (self.manufactured_year != None):
            self.age = int(datetime.datetime.now().year) - self.manufactured_year
        else:
            self.age = None

    def filter_asset(self):
        self.derived_filter_asset()

    def derived_filter_asset(self):
        pass

    def dump(self):
        print("Asset Type: " + type(self).__name__)
        print("Make: " + str(self.make))
        print("Model: " + str(self.model))
        print("Serial: " + str(self.serial))
        print("Year: " + str(self.manufactured_year))
        print("Age: " + str(self.age))
        self.derived_dump()
        print()

    def derived_dump(self):
        pass