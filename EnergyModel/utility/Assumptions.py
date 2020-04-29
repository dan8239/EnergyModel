class Assumptions():
    #"Class representing assumptions made during modeling"
    def __init__(self):
        self.r22_certainty_age = 2010 #Year before which R22 is assumed
        self.r22_implied_age = 12     #R22 Refrig RTU implied age
        self.r410_implied_age = 3     #R410 Refrig RTU implied age
        self.eer_degradation_factor = 0.015   #per year eer penalty
        self.existing_RTU_min_eer = 6.0 #minimum assumed eer for existing units
        self.no_info_eer = 10    #eer for units with no EER or age listed
        self.eer_degredation_method = "Compound"   #method EER is degraded by. Compound, yearly, or no degradation
        self.existing_RTU_no_data_econ = False #value of economizer without data
        self.existing_RTU_no_data_vfd = False #value of vfd without data
        self.existing_RTU_no_data_staged_cmp = False #value of staged compressors without data
        self.new_RTU_no_data_econ = False #value of economizer without data
        self.new_RTU_no_data_vfd = False #value of vfd without data
        self.new_RTU_no_data_staged_cmp = False #value of staged compressors without data
        self.retrofit_efficiency_gain = 0.3 #eer efficiency gained by retrofit (%)
        self.new_RTU_min_eer = 11.76 #minimum eer for new units (if none proposed)
        self.new_RTU_fan_efficiency = 0.90     #replacement fan efficiency increase over existing
        self.existing_RTU_no_data_maintenance = "OK" #condition of existing unit if none listed
        self.existing_RTU_poor_maintenance_values = ["Poor", "Marginal"]
        

