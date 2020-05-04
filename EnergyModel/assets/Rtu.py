import pandas as pd
import numpy as np
from assets import Asset
from utility import UtilityFunctions, TableAgeEfficiency, Assumptions
import datetime
from enumsets import FanSeq

class Rtu(Asset.Asset):
    def __init__(self, proposal = None, auid = 0, tons = 0, evap_hp = 0, fact_eer = 0, econ = False, refrig_type = None, cmp_stg = 1):
        super().__init__()
        self.tons = tons
        self.evap_hp = evap_hp
        self.fact_eer = fact_eer
        self.degr_eer = 0
        self.econ = econ
        self.refrig_type = refrig_type
        self.cmp_stg = cmp_stg
        #move this section to assumptions! Separate assumptions file into Asset types!
        self.fan_stg = Assumptions.RtuDefaults.fan_stg
        self.clg_fan_cntrl_seq = Assumptions.RtuDefaults.clg_fan_cntrl_seq
        self.htg_fan_cntrl_seq = Assumptions.RtuDefaults.htg_fan_cntrl_seq
        self.vent_fan_cntrl_seq = Assumptions.RtuDefaults.vent_fan_cntrl_seq
        self.fan_efficiency = Assumptions.RtuDefaults.fan_efficiency
        self.occ_htg_sp = Assumptions.RtuDefaults.occ_htg_sp
        self.unocc_htg_sp = Assumptions.RtuDefaults.unocc_htg_sp
        self.occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp
        self.unocc_clg_sp = Assumptions.RtuDefaults.unocc_clg_sp
        self.min_oa_pct = Assumptions.RtuDefaults.min_oa_pct
        self.vent_fan_min_speed = Assumptions.RtuDefaults.vent_fan_min_speed
        self.vent_fan_max_speed = Assumptions.RtuDefaults.vent_fan_max_speed
        self.clg_fan_min_speed = Assumptions.RtuDefaults.clg_fan_min_speed
        self.clg_fan_max_speed = Assumptions.RtuDefaults.clg_fan_max_speed
        self.htg_fan_min_speed = Assumptions.RtuDefaults.htg_fan_min_speed
        self.htg_fan_max_speed = Assumptions.RtuDefaults.htg_fan_max_speed
        self.clg_design_factor = Assumptions.RtuDefaults.clg_design_factor
        self.htg_design_factor = Assumptions.RtuDefaults.htg_design_factor
        self.cmp_lockout_temp = Assumptions.RtuDefaults.cmp_lockout_temp
        #Move this stuff into an energy object (subtype RTU energy object w/fan and refrig disaggregated)
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
        self.refrig_type = asset_to_copy.refrig_type
        self.cmp_stg = asset_to_copy.cmp_stg
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
                self.age = Assumptions.FilterAssets.r22_implied_age
            else:
                self.age = Assumptions.FilterAssets.r410_implied_age

    def __fill_refrig_type_by_year(self):
        #if manufactured before certain date (2010 default), assume R22
        if (self.refrig_type == None):
            if (self.manufactured_year != None and self.manufactured_year < Assumptions.FilterAssets.r22_certainty_year):
                self.refrig_type == "R-22"

    def __fill_eer_by_age(self):
        #if no eer listed, determine approx eer from age
        if (self.fact_eer == None or self.fact_eer == 0 or self.fact_eer == np.nan):
            if (self.age != None):
                eer_tbl = TableAgeEfficiency.TableAgeEfficiency.get_table()
                row = eer_tbl[eer_tbl['AGE'] == self.age]
                self.fact_eer = row.EER.iloc[0]
            else:
                self.fact_eer = Assumptions.FilterAssets.no_info_eer

    def __fill_evap_hp_by_tonnage(self):
        #if no eer listed, determine approx eer from age
        if (self.evap_hp == None or self.evap_hp == 0 or self.evap == np.nan):
            if (self.tons != None):
                self.evap_hp = Assumptions.FilterAssets.evap_hp_per_ton * self.tons
            else:
                self.evap_hp = 0

    def __degrade_eer(self):
        #calculate degraded eer
        if (Assumptions.FilterAssets.eer_degredation_method == "Compound"):
            self.degr_eer = UtilityFunctions.UtilityFunctions.degrade_eer_compound(self.fact_eer, self.age, Assumptions.FilterAssets.eer_degradation_factor, Assumptions.FilterAssets.existing_RTU_min_eer)
        elif(Assumptions.FilterAssets.eer_degredation_method == "Yearly"):
            self.degr_eer = UtilityFunctions.UtilityFunctions.degrade_eer_yearly(self.fact_eer, self.age, Assumptions.FilterAssets.eer_degradation_factor, Assumptions.FilterAssets.existing_RTU_min_eer)
        else:
            self.degr_eer = self.fact_eer

    #fill data that is able to be inferred from known information
    def _filter_existing_asset(self):
        self.__fill_age_by_refrig_type()
        self.__fill_refrig_type_by_year()
        self.__fill_eer_by_age()
        self.__fill_evap_hp_by_tonnage()
        self.__degrade_eer()
        
   
    def _filter_new_asset(self):
        #if r22 is refrigerant type, assume age
        self.manufactured_year = datetime.datetime.now().year
        self.age = 0

        #set refrig type
        self.refrig_type = "R-410A"
        
        #set horsepower
        self.__fill_evap_hp_by_tonnage()

        #if not listed, set eer to minimum new unit eer
        if (self.fact_eer == None or self.fact_eer == 0 or self.fact_eer == np.nan):
            self.fact_eer = Assumptions.FilterAssets.new_RTU_min_eer
        self.degr_eer = self.fact_eer

        

        #set fan efficiency for new unit
        self.fan_efficiency = Assumptions.FilterAssets.new_RTU_fan_efficiency
    

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
        self.clg_fan_cntrl_seq = row.x_fan_seq
        self.vent_fan_cntrl_seq = row.x_fan_seq
        self.cmp_stg = row.x_cmp_stg
        self.evap_hp = row.x_evap_hp

    def _derived_copy_new_asset_from_row(self, row):
        self.tons = row.n_tonnage
        self.econ = row.n_economizer
        self.fact_eer = row.n_eer
        self.clg_fan_cntrl_seq = row.n_fan_seq
        self.vent_fan_cntrl_seq = row.n_fan_seq
        self.cmp_stg = row.n_cmp_stg
        self.evap_hp = row.n_evap_hp
    
    '''
    def __update_vfd_selection(self):
        if (self.vfd == True):
            self.vent_fan_cntrl_seq = "VFD"
            self.clg_fan_cntrl_seq = "VFD"
            self.htg_fan_cntrl_seq = "VFD"
        else:
            self.vent_fan_cntrl_seq = "CFD"
            self.clg_fan_cntrl_seq = "CFD"
            self.htg_fan_cntrl_seq = "CFD"
    '''

    def _derived_dump(self):
        print("Tons: " + str(self.tons))
        #print("Factory EER:" + str(self.fact_eer))
        print("Degraded EER: " + str(self.degr_eer))
        print("Econ: %s" %self.econ)
        print("Fan Seq: %s" %self.clg_fan_cntrl_seq)
        print("Staged Compressors: %s" %self.cmp_stg)
        print()


