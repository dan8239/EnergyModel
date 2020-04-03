import UtilityFunctions
import pandas as pd
from Asset import *

class Rtu(Asset):
    def __init__(self, site = None, auid = 0, tons = 0, eer = 0, econ = False, vfd = False, refrig_type = None, stg_cmp = False):
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
        if (self.filtered_asset.age == None):
            if (self.filtered_asset.refrig_type == "R-22" or self.filtered_asset.refrig_type == "R-12"):
                self.filtered_asset.age = self.proposal.site.assumptions.r22_implied_age
            else:
                self.filtered_asset.age = self.proposal.site.assumptions.r410_implied_age
        #if manufactured before certain date (2010 default), assume R22
        if (self.filtered_asset.refrig_type == None):
            if (self.filtered_asset.manufactured_year != None and self.filtered_asset.manufactured_year < self.proposal.site.assumptions.r22_certainty_age):
                self.filtered_asset.refrig_type == "R-22"
        #if no eer listed, determine approx eer from age
        if (self.filtered_asset.eer == None):
            if (self.filtered_asset.age != None):
                eer_table = pd.read_csv("EER-BY-YEAR.csv")
                age_table = eer_table['EER'].where(eer_table['AGE'] == self.filtered_asset.age)
                approx_age = age_table[0]
            else:
                self.filtered_asset.eer = self.proposal.site.assumptions.no_info_eer

    def derived_dump(self):
        print("Tons: " + str(self.tons))
        print("EER: " + str(self.eer))
        print("Econ: %s" %self.econ)
        print("VFD: %s" %self.vfd)
        print("Staged Compressors: %s" %self.stg_cmp)
        print()


