import pandas as pd
import numpy as np
from assets import Asset
from utility import UtilityFunctions, TableAgeEfficiency
import datetime

class Rtu(Asset.Asset):
    def __init__(self, proposal = None, auid = 0, tons = 0, evap_hp = 0, fact_eer = 0, econ = False, vfd = False, refrig_type = None, stg_cmp = 1):
        super().__init__()
        self.tons = tons
        self.evap_hp = evap_hp
        self.fact_eer = fact_eer
        self.degr_eer = 0
        self.econ = econ
        self.vfd = vfd
        self.refrig_type = refrig_type
        self.stg_cmp = stg_cmp
        self.fan_efficiency = 0.85
        self.occ_htg_sp = 68
        self.unocc_htg_sp = 55
        self.occ_clg_sp = 72
        self.unocc_clg_sp = 85
        self.min_oa_pct = .12
        self.vent_fan_min_speed = 0.7
        self.vent_fan_max_speed = 1.0
        self.clg_fan_min_speed = 0.7
        self.clg_fan_max_speed = 1.0
        self.htg_fan_min_speed = 1.0
        self.htg_fan_max_speed = 1.0
        self.cmp_lockout_temp = 50
        self.__update_vfd_selection()
        self.fan_vent_kwh_yearly = 0
        self.fan_clg_kwh_yearly = 0
        self.fan_htg_kwh_yearly = 0
        self.fan_kwh_yearly = 0
        self.refrg_kwh_yearly = 0

    def _derived_copy_asset(self, asset_to_copy):
        self.tons = asset_to_copy.tons
        self.evap_hp = asset_to_copy.evap_hp
        self.fact_eer = asset_to_copy.fact_eer
        self.degr_eer = asset_to_copy.degr_eer
        self.econ = asset_to_copy.econ
        self.vfd = asset_to_copy.vfd
        self.refrig_type = asset_to_copy.refrig_type
        self.stg_cmp = asset_to_copy.stg_cmp
        self.occ_htg_sp = asset_to_copy.occ_htg_sp
        self.unocc_htg_sp = asset_to_copy.unocc_htg_sp
        self.occ_clg_sp = asset_to_copy.occ_clg_sp
        self.unocc_clg_sp = asset_to_copy.unocc_clg_sp
        self.min_oa_pct = asset_to_copy.min_oa_pct
        self.vent_fan_min_speed = asset_to_copy.vent_fan_min_speed
        self.vent_fan_max_speed = asset_to_copy.vent_fan_max_speed
        self.vent_fan_cntrl_seq = asset_to_copy.vent_fan_cntrl_seq
        self.clg_fan_min_speed = asset_to_copy.clg_fan_min_speed
        self.clg_fan_max_speed = asset_to_copy.clg_fan_max_speed
        self.clg_fan_cntrl_seq = asset_to_copy.clg_fan_cntrl_seq
        self.htg_fan_min_speed = asset_to_copy.htg_fan_min_speed
        self.htg_fan_max_speed = asset_to_copy.htg_fan_max_speed
        self.htg_fan_cntrl_seq = asset_to_copy.htg_fan_cntrl_seq
        self.cmp_lockout_temp = asset_to_copy.cmp_lockout_temp

    def __fill_age_by_refrig_type(self):
        #if r22 is refrigerant type, assume age
        if (self.age == None or self.age > 50):
            if (self.refrig_type == "R-22" or self.refrig_type == "R-12"):
                self.age = self.proposal.site.assumptions.r22_implied_age
            else:
                self.age = self.proposal.site.assumptions.r410_implied_age

    def __fill_refrig_type_by_year(self):
        #if manufactured before certain date (2010 default), assume R22
        if (self.refrig_type == None):
            assumptions = self.proposal.site.assumptions
            if (self.manufactured_year != None and self.manufactured_year < assumptions.r22_certainty_age):
                self.refrig_type == "R-22"

    def __fill_eer_by_age(self):
        #if no eer listed, determine approx eer from age
        if (self.fact_eer == None or self.fact_eer == 0 or self.fact_eer == np.nan):
            if (self.age != None):
                eer_tbl = TableAgeEfficiency.TableAgeEfficiency.get_table()
                row = eer_tbl[eer_tbl['AGE'] == self.age]
                self.fact_eer = row.EER.iloc[0]
            else:
                self.fact_eer = self.proposal.site.assumptions.no_info_eer

    def __degrade_eer(self):
        #calculate degraded eer
        assumptions = self.proposal.site.assumptions
        if (assumptions.eer_degredation_method == "Compound"):
            self.degr_eer = UtilityFunctions.UtilityFunctions.degrade_eer_compound(self.fact_eer, self.age, assumptions.eer_degradation_factor, assumptions.existing_RTU_min_eer)
        elif(assumptions.eer_degredation_method == "Yearly"):
            self.degr_eer = UtilityFunctions.UtilityFunctions.degrade_eer_yearly(self.fact_eer, self.age, assumptions.eer_degradation_factor, assumptions.existing_RTU_min_eer)
        else:
            self.degr_eer = self.fact_eer

    #fill data that is able to be inferred from known information
    def _filter_existing_asset(self):
        self.__fill_age_by_refrig_type()
        self.__fill_refrig_type_by_year()
        self.__fill_eer_by_age()
        self.__degrade_eer()
        
   
    def _filter_new_asset(self):
        #if r22 is refrigerant type, assume age
        self.manufactured_year = datetime.datetime.now().year
        self.age = 0

        #get assumptions reference
        assumptions = self.proposal.site.assumptions

        #set refrig type
        self.refrig_type = "R-410A"

        #if not listed, set eer to minimum new unit eer
        if (self.fact_eer == None or self.fact_eer == 0 or self.fact_eer == np.nan):
            self.fact_eer = assumptions.new_RTU_min_eer
        self.degr_eer = self.fact_eer

        #set fan efficiency for new unit
        self.fan_efficiency = assumptions.new_RTU_fan_efficiency
    

    # Filter through asset data and fill gaps based on model assumptions
    def _derived_filter_asset(self):
        if (self.status == "existing"):
            self._filter_existing_asset()
        elif (self.status == "new"):
            self._filter_new_asset()
        else:
            raise TypeError("Missing status for asset: " + str(type(self)))
    
    def _derived_copy_existing_asset_from_row(self, row):
        self.tons = row.x_tonnage
        self.econ = row.x_economizer
        self.fact_eer = row.x_eer
        self.refrig_type = row.x_refrig_type
        self.vfd = row.x_vfd
        self.stg_cmp = row.x_cmp_stg
        self.evap_hp = row.x_evap_hp
        self.__update_vfd_selection()

    def _derived_copy_new_asset_from_row(self, row):
        self.tons = row.n_tonnage
        self.econ = row.n_economizer
        self.fact_eer = row.n_eer
        self.vfd = row.n_vfd
        self.stg_cmp = row.n_cmp_stg
        self.evap_hp = row.n_evap_hp
        self.__update_vfd_selection()
    
    def __update_vfd_selection(self):
        if (self.vfd == True):
            self.vent_fan_cntrl_seq = "VFD"
            self.clg_fan_cntrl_seq = "VFD"
            self.htg_fan_cntrl_seq = "VFD"
        else:
            self.vent_fan_cntrl_seq = "CFD"
            self.clg_fan_cntrl_seq = "CFD"
            self.htg_fan_cntrl_seq = "CFD"

    def _derived_dump(self):
        print("Tons: " + str(self.tons))
        #print("Factory EER:" + str(self.fact_eer))
        print("Degraded EER: " + str(self.degr_eer))
        print("Econ: %s" %self.econ)
        print("VFD: %s" %self.vfd)
        print("Staged Compressors: %s" %self.stg_cmp)
        print()


