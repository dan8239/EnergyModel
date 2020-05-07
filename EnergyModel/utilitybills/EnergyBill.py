from enum import Enum
import numpy as np
import pandas as pd

class BillDuration(Enum):
    """Bill Duration Enumeration"""
    YEARLY = 0
    MONTHLY = 1

class EnergyBill():
    """description of class"""
    def __init__(self, bill_duration = BillDuration.YEARLY):
        self.site = None
        self.reliable = False
        self.unit = None
        self.bill_type = None
        self.bill_duration = bill_duration
        self.annual_units = 0
        self.annual_dollars = 0
        self.dollars_per_unit = 0

    def to_dataframe(self):
        colnames = vars(self).keys()    #vars gets dict from object. Keys gets keys from dict key-value pairs
        df = pd.DataFrame([[getattr(self, j) for j in colnames]], columns = colnames) #get attributes in a row
        df = df.drop(['reliable','bill_duration','bill_type'], axis = 1)   #drop unecessary columns
        df['annual_units'].add_prefix(str(self.bill_type) + "_")
        df['annual_dollars'].add_prefix(str(self.bill_type) + "_")
        df['dollars_per_unit'].add_prefix(str(self.bill_type) + "_")
        df['unit'].add_prefix(str(self.bill_type) + "_")
        df['site'] = self.site.id
        return df

    def import_from_file(self, dataframe):
        raise TypeError("Derived Class Method Not Implemented")
        

    def calc_rate(self):
        if (self.annual_dollars == 0 or
            self.annual_units == 0):
            raise TypeError("Tried to Calculate Rate of Unreliable Bill")
        self.dollars_per_unit = self.annual_dollars / self.annual_units

    def set_reliable(self):
        self.reliable = True

    def set_unreliable(self):
        self.reliable = False

class ElectricBill(EnergyBill):
    def __init__(self, bill_duration = BillDuration.YEARLY):
        super().__init__(bill_duration)
        self.bill_type = "electric"
        self.unit = "kwh"

    def import_from_row(self, row):  
        if (np.isnan(row.annual_electric_kwh) or 
            np.isnan(row.annual_electric_dollars) or 
            row.annual_electric_kwh == 0 or 
            row.annual_electric_dollars == 0):
            self.annual_units = 0
            self.annual_dollars = 0
            self.dollars_per_unit = 0
            self.set_unreliable()
        else:
            self.set_reliable()
            self.annual_units = row.annual_electric_kwh
            self.annual_dollars = row.annual_electric_dollars
            self.calc_rate()

class NaturalGasBill(EnergyBill):
    def __init__(self, bill_duration = BillDuration.YEARLY):
        super().__init__(bill_duration)
        self.bill_type = "natural gas"
        self.unit = "therms"



