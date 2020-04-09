class UtilityFunctions():
    
    def degrade_eer_compound(eer, age, maint_factor, min_eer):
        return max(min_eer,eer*(1-maint_factor)**age)

    def degrade_eer_yearly(eer, age, maint_factor, min_eer):
        return max(min_eer,(eer - age*maint_factor))
