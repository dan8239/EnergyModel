import UtilityFunctions
import pandas as pd
from TableAgeEfficiency import *
from Asset import *

class Rtu(Asset):
    def __init__(self, proposal = None, auid = 0, tons = 0, eer = 0, econ = False, vfd = False, refrig_type = None, stg_cmp = False):
        super().__init__()
        self.tons = tons
        self.eer = eer
        self.econ = econ
        self.vfd = vfd
        self.refrig_type = refrig_type
        self.stg_cmp = stg_cmp

    # Filter through asset data and fill gaps based on model assumptions
    def derived_filter_asset(self):
        #if r22 is refrigerant type, assume age
        if (self.age == None):
            if (self.refrig_type == "R-22" or self.refrig_type == "R-12"):
                self.age = self.proposal.site.assumptions.r22_implied_age
            else:
                self.age = self.proposal.site.assumptions.r410_implied_age
        #if manufactured before certain date (2010 default), assume R22
        if (self.refrig_type == None):
            if (self.manufactured_year != None and self.manufactured_year < self.proposal.site.assumptions.r22_certainty_age):
                self.refrig_type == "R-22"
        #if no eer listed, determine approx eer from age
        if (self.eer == None or self.eer == 0):
            if (self.age != None):
                eer_tbl = TableAgeEfficiency.get_table()
                row = eer_tbl[eer_tbl['AGE'] == self.age]
                if (self.proposal.site.assumptions.eer_degredation_method == "Compound"):
                    self.eer = row.COMPOUND_DEGR.iloc[0]
                elif(self.proposal.site.assumptions.eer_degredation_method == "Yearly"):
                    self.eer = row.YEARLY_DEGR.iloc[0]
                elif(self.proposal.site.assumptions.eer_degredation_method == "Factory"):
                    self.eer = row.EER.iloc[0]
            else:
                self.eer = self.proposal.site.assumptions.no_info_eer
            test = self.eer

    def derived_dump(self):
        print("Tons: " + str(self.tons))
        print("EER: " + str(self.eer))
        print("Econ: %s" %self.econ)
        print("VFD: %s" %self.vfd)
        print("Staged Compressors: %s" %self.stg_cmp)
        print()


