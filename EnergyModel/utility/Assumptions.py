from enumsets import FanSeq

class FilterAssets():
    r22_certainty_year = 2010 #Year before which R22 is assumed
    r22_implied_age = 12     #R22 Refrig RTU implied age
    r410_implied_age = 3     #R410 Refrig RTU implied age
    eer_degradation_factor = 0.015   #per year eer penalty
    existing_RTU_min_eer = 6.0 #minimum assumed eer for existing units
    no_info_eer = 10    #eer for units with no EER or age listed
    eer_degredation_method = "Compound"   #method EER is degraded by. Compound, yearly, or no degradation
    existing_RTU_no_data_econ = False #value of economizer without data
    existing_RTU_no_data_fan_seq = FanSeq.FanSeq.CONSTANT_SPEED #value of vfd without data
    existing_RTU_no_data_staged_cmp = False #value of staged compressors without data
    new_RTU_no_data_econ = False #value of economizer without data
    new_RTU_no_data_ = FanSeq.FanSeq.CONSTANT_SPEED #value of vfd without data
    new_RTU_no_data_staged_cmp = False #value of staged compressors without data
    retrofit_efficiency_gain = 0.3 #eer efficiency gained by retrofit (%)
    new_RTU_min_eer = 11.76 #minimum eer for new units (if none proposed)
    new_RTU_fan_efficiency = 0.90     #replacement fan efficiency increase over existing
    existing_RTU_no_data_maintenance = "OK" #condition of existing unit if none listed
    existing_RTU_poor_maintenance_values = ["Poor", "Marginal"]
    evap_hp_per_ton = 0.30  #horsepower of fan per ton when no data available (source is asset database averages)

class RtuDefaults():
    fan_efficiency = 0.85
    occ_htg_sp = 68
    unocc_htg_sp = 60
    occ_clg_sp = 72
    unocc_clg_sp = 80
    min_oa_pct = .12
    htg_design_temp = 5
    clg_design_temp = 95
    vent_fan_min_speed = 0.333
    vent_fan_max_speed = 1.0
    clg_fan_min_speed = 0.333
    clg_fan_max_speed = 1.0
    htg_fan_min_speed = 1.0
    htg_fan_max_speed = 1.0
    clg_design_factor = 0.2
    htg_design_factor = 0.4
    cmp_lockout_temp = 50
    fan_stg = 2 # only applies when fan sequence is staged
    clg_fan_cntrl_seq = FanSeq.FanSeq.CONSTANT_SPEED
    htg_fan_cntrl_seq = FanSeq.FanSeq.CONSTANT_SPEED
    vent_fan_cntrl_seq = FanSeq.FanSeq.CONSTANT_SPEED
        
class ClimateDefaults():
    occ_clg_balance_point_temp = 56.0
    occ_htg_balance_point_temp = 52.0
    unocc_load_reduction = 0.9  #percent of load reduced when unoccupied (lighting, people, some plug)

        #heating load approx = htg_sp - htg_balance
    #heating load reduced when unoccupied by some percent (lighting, people, some plug)
    #balance point increase partially offset by setpoint adjustment
    def calc_unocc_htg_balance_point_temp(occ_htg_balance_point_temp, occ_htg_sp, unocc_htg_sp, unocc_load_reduction):
        return occ_htg_balance_point_temp + unocc_load_reduction*(occ_htg_sp - occ_htg_balance_point_temp) - (occ_htg_sp - unocc_htg_sp)

    #cooling load approx = clg_sp - clg_balance
    #heating load reduced when unoccupied by some percent (lighting, people, some plug)
    #balance point increases from temp setpoint delta as well
    def calc_unocc_clg_balance_point_temp(occ_clg_balance_point_temp, occ_clg_sp, unocc_clg_sp, unocc_load_reduction):
        return occ_clg_balance_point_temp + unocc_load_reduction*(occ_clg_sp - occ_clg_balance_point_temp) + (unocc_clg_sp - occ_clg_sp)


    unocc_clg_balance_point_temp = calc_unocc_clg_balance_point_temp(occ_clg_balance_point_temp, RtuDefaults.occ_clg_sp, RtuDefaults.unocc_clg_sp, unocc_load_reduction)
    unocc_htg_balance_point_temp = calc_unocc_htg_balance_point_temp(occ_htg_balance_point_temp, RtuDefaults.occ_htg_sp, RtuDefaults.unocc_htg_sp, unocc_load_reduction)
    

