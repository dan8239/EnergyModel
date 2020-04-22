import pandas as pd
from assets import Asset
from utility import UtilityFunctions, TableAgeEfficiency
import datetime

class Rtu(Asset.Asset):
    def __init__(self, proposal = None, auid = 0, tons = 0, evap_hp = 0, fact_eer = 0, econ = False, vfd = False, refrig_type = None, stg_cmp = False):
        super().__init__()
        self.tons = tons
        self.evap_hp = evap_hp
        self.fact_eer = fact_eer
        self.degr_eer = 0
        self.econ = econ
        self.vfd = vfd
        self.refrig_type = refrig_type
        self.stg_cmp = stg_cmp

    def _derived_copy_asset(self, asset_to_copy):
        self.tons = asset_to_copy.tons
        self.fact_eer = asset_to_copy.fact_eer
        self.degr_eer = asset_to_copy.degr_eer
        self.econ = asset_to_copy.econ
        self.vfd = asset_to_copy.vfd
        self.refrig_type = asset_to_copy.refrig_type
        self.stg_cmp = asset_to_copy.stg_cmp
    
    def _filter_existing_asset(self):
        #get assumptions reference
        assumptions = self.proposal.site.assumptions
        #if r22 is refrigerant type, assume age
        if (self.age == None):
            if (self.refrig_type == "R-22" or self.refrig_type == "R-12"):
                self.age = assumptions.r22_implied_age
            else:
                self.age = assumptions.r410_implied_age
        #if manufactured before certain date (2010 default), assume R22
        if (self.refrig_type == None):
            if (self.manufactured_year != None and self.manufactured_year < assumptions.r22_certainty_age):
                self.refrig_type == "R-22"
        #if no eer listed, determine approx eer from age
        if (self.fact_eer == None or self.fact_eer == 0):
            if (self.age != None):
                eer_tbl = TableAgeEfficiency.TableAgeEfficiency.get_table()
                row = eer_tbl[eer_tbl['AGE'] == self.age]
                self.fact_eer = row.EER.iloc[0]
                if (assumptions.eer_degredation_method == "Compound"):
                    self.degr_eer = UtilityFunctions.UtilityFunctions.degrade_eer_compound(self.fact_eer, self.age, assumptions.eer_degradation_factor, assumptions.existing_RTU_min_eer)
                elif(assumptions.eer_degredation_method == "Yearly"):
                    self.degr_eer = UtilityFunctions.UtilityFunctions.degrade_eer_yearly(self.fact_eer, self.age, assumptions.eer_degradation_factor, assumptions.existing_RTU_min_eer)
                else:
                    self.degr_eer = self.fact_eer
            else:
                self.eer = self.proposal.site.assumptions.no_info_eer

    def _filter_new_asset(self):
        #if r22 is refrigerant type, assume age
        self.manufactured_year = datetime.datetime.now().year
        self.age = 0

        #get assumptions reference
        assumptions = self.proposal.site.assumptions

        #set refrig type
        self.refrig_type = "R-410A"
        if (self.fact_eer == None or self.fact_eer == 0):
            self.fact_eer = assumptions.new_RTU_min_eer
        self.degr_eer = self.fact_eer


    # Filter through asset data and fill gaps based on model assumptions
    def _derived_filter_asset(self):
        if (self.status == "existing"):
            self._filter_existing_asset()
        elif (self.status == "new"):
            self._filter_new_asset()
        else:
            raise TypeError("Missing status for asset: " + str(type(self)))
        

    def _derived_dump(self):
        print("Tons: " + str(self.tons))
        print("Factory EER:" + str(self.fact_eer))
        print("Degraded EER: " + str(self.degr_eer))
        print("Econ: %s" %self.econ)
        print("VFD: %s" %self.vfd)
        print("Staged Compressors: %s" %self.stg_cmp)
        print()


