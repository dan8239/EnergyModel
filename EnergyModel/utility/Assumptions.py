class FilterAssets():
    r22_certainty_year = 2010 #Year before which R22 is assumed
    r22_implied_age = 12     #R22 Refrig RTU implied age
    r410_implied_age = 3     #R410 Refrig RTU implied age
    eer_degradation_factor = 0.015   #per year eer penalty
    existing_RTU_min_eer = 6.0 #minimum assumed eer for existing units
    no_info_eer = 10    #eer for units with no EER or age listed
    eer_degredation_method = "Compound"   #method EER is degraded by. Compound, yearly, or no degradation
    existing_RTU_no_data_econ = False #value of economizer without data
    existing_RTU_no_data_vfd = False #value of vfd without data
    existing_RTU_no_data_staged_cmp = False #value of staged compressors without data
    new_RTU_no_data_econ = False #value of economizer without data
    new_RTU_no_data_vfd = False #value of vfd without data
    new_RTU_no_data_staged_cmp = False #value of staged compressors without data
    retrofit_efficiency_gain = 0.3 #eer efficiency gained by retrofit (%)
    new_RTU_min_eer = 11.76 #minimum eer for new units (if none proposed)
    new_RTU_fan_efficiency = 0.90     #replacement fan efficiency increase over existing
    existing_RTU_no_data_maintenance = "OK" #condition of existing unit if none listed
    existing_RTU_poor_maintenance_values = ["Poor", "Marginal"]

class RtuDefaults():
    fan_efficiency = 0.85
    occ_htg_sp = 68
    unocc_htg_sp = 55
    occ_clg_sp = 72
    unocc_clg_sp = 85
    min_oa_pct = .12
    vent_fan_min_speed = 0.7
    vent_fan_max_speed = 1.0
    clg_fan_min_speed = 0.7
    clg_fan_max_speed = 1.0
    htg_fan_min_speed = 1.0
    htg_fan_max_speed = 1.0
    clg_design_factor = 0.2
    htg_design_factor = 0.4
    cmp_lockout_temp = 50
    clg_design_factor = 0.2
    htg_design_factor = 0.4
        

