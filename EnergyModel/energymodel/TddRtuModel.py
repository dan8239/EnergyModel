from assets import Rtu, Cdu, Pkg

class TddRtuModel():
    """description of class"""
    def __init__(self):
        super().__init__()
        self.load_factor = 0.8
        self.kw_per_bhp = 0.7457
        self.clg_design_factor = 0.2
        self.htg_design_factor = 0.4
        self.max_cycling_degradation = 0.07
        self.fan_cube_law_factor = 3

    #based on efficiency curve. Efficiency 100% at 95 deg F, 65.060241% at 65 deg F 
    def __refrig_kw_draw_pct_calc(self, rtu, ea_t):
        return 0.011646586*max(rtu.cmp_lockout_temp, ea_t) - 0.106435703

    #based on thermal output curve. Thermal output 100% at 95 deg F, 114% at 65 deg F
    def __refrig_therm_eff_pct_calc(self, rtu, ea_t):
        return -0.0046666667*max(rtu.cmp_lockout_temp, ea_t) + 1.44333333

    def __vent_fan_speed(self, rtu):
        if rtu.vent_fan_cntrl_seq == "CFD":
            avg_vent_fan_speed = rtu.vent_fan_max_speed
        else:
            avg_vent_fan_speed = rtu.vent_fan_min_speed
        return avg_vent_fan_speed

    def __clg_fan_speed(self, rtu, avg_clg_therm_load_pct):
        if (rtu.clg_fan_cntrl_seq == "CFD"):
            avg_clg_fan_speed = rtu.clg_fan_max_speed
        else:
            avg_clg_fan_speed = avg_clg_therm_load_pct * (rtu.clg_fan_max_speed - rtu.clg_fan_min_speed) + rtu.clg_fan_min_speed
        return avg_clg_fan_speed

    def __htg_fan_speed(self, rtu, avg_htg_therm_load_pct):
        if (rtu.htg_fan_cntrl_seq == "CFD"):
            avg_htg_fan_speed = rtu.htg_fan_max_speed
        else:
            avg_htg_fan_speed = avg_htg_therm_load_pct * (rtu.htg_fan_max_speed - rtu.htg_fan_min_speed) + rtu.htg_fan_min_speed
        return avg_htg_fan_speed


    def calculate(self, rtu):
        print("Running energy calculations for proposal " + rtu.proposal.prop_id + " " + rtu.status + " RTU")
        if ((isinstance(rtu, Cdu.Cdu) or isinstance(rtu, Pkg.Pkg)) and rtu.tons > 0):
            #easy reference to climate object
            cd = rtu.proposal.site.climate_data

            #peak load calculations
            #break horsepower from list hp
            bhp = rtu.evap_hp * self.load_factor
            #peak fan kwh from bhp to kwh conversion
            fan_peak_kwh = bhp * self.kw_per_bhp / rtu.fan_efficiency
            #Peak fan kw/ton
            fan_peak_kw_per_ton = fan_peak_kwh / rtu.tons
            #peak RTU kw/ton from eer (total fan + refrigeration @ design)
            rtu_peak_kw_per_ton = 12 / rtu.degr_eer
            #peak refrig kw/ton, total - fan
            refrig_peak_kw_per_ton = rtu_peak_kw_per_ton - fan_peak_kw_per_ton

            #avg clg load condition calculations (REFRIGERATION)
            #cooling mixed air temperature. If no econ, use zone temp, if econ, use lower of MA-T and OA-T
            if (rtu.econ == False):
                clg_ma_t = rtu.occ_clg_sp
            else:
                min_oa_clg_ma_t = rtu.min_oa_pct * (cd.avg_clg_oa_t) + (1-rtu.min_oa_pct) * (rtu.occ_clg_sp)
                clg_ma_t = min(min_oa_clg_ma_t, cd.avg_clg_oa_t)
            #refrig % of peak draw at entering air conditions
            refrig_kw_draw_pct_at_ea_t = self.__refrig_kw_draw_pct_calc(rtu, clg_ma_t)
            #refrig efficiency gain at entering air conditions
            refrig_eff_pct_at_ea_t = self.__refrig_therm_eff_pct_calc(rtu, clg_ma_t)
            #peak thermal load percentage taking design factor into account
            refrig_peak_therm_load_pct = 1 / (1 + self.clg_design_factor)
            #thermal load percentage at avg condition, adding in efficiency gain of refrigeration
            ### Use For Fan Calcs###
            refrig_therm_load_pct_at_oa_t = refrig_peak_therm_load_pct / refrig_eff_pct_at_ea_t * cd.avg_clg_load_pct
            #cycling on low load kw draw penalty. Divide penalty by number of compressors
            refrig_kw_draw_pct_cycling_penalty = 1 + (1-refrig_therm_load_pct_at_oa_t) * self.max_cycling_degradation / rtu.stg_cmp
            #total refrigeration draw when running at condition
            refrig_kw_per_ton_at_oa_t = refrig_peak_kw_per_ton * refrig_kw_draw_pct_at_ea_t * refrig_kw_draw_pct_cycling_penalty

            #occ hours calculations
            #refrigeration runtime raw
            eflh_c_occ = cd.eflh_c * rtu.run_hours_yearly / 8760
            #reduce refrigeration hours for thermal efficiency increase
            eflh_c_occ_eff = eflh_c_occ / refrig_eff_pct_at_ea_t
            #fan heating run hours
            fan_htg_run_hours = cd.htg_hrs * cd.avg_htg_load_pct
            fan_htg_run_hours_occ = fan_htg_run_hours * rtu.run_hours_yearly / 8760
            #fan cooling run hours
            fan_clg_run_hours = cd.clg_hrs * cd.avg_clg_load_pct
            fan_clg_run_hours_occ = fan_clg_run_hours * rtu.run_hours_yearly / 8760
            #vent run hours
            fan_vent_run_hours = 8760 - fan_htg_run_hours - fan_clg_run_hours
            fan_vent_run_hours_occ = fan_vent_run_hours * rtu.run_hours_yearly / 8760

            #fan speed calculations
            fan_avg_vent_speed = self.__vent_fan_speed(rtu)
            fan_avg_clg_speed = self.__clg_fan_speed(rtu, refrig_therm_load_pct_at_oa_t)
            fan_avg_htg_speed = self.__htg_fan_speed(rtu, cd.avg_htg_load_pct)
            #fan kw/ton calculations (fan cube law)
            fan_avg_vent_kw_per_ton = fan_peak_kw_per_ton * fan_avg_vent_speed ** self.fan_cube_law_factor
            fan_avg_clg_kw_per_ton = fan_peak_kw_per_ton * fan_avg_clg_speed ** self.fan_cube_law_factor
            fan_avg_htg_kw_per_ton = fan_peak_kw_per_ton * fan_avg_htg_speed ** self.fan_cube_law_factor

            #fan usage calcs (runtime * avg kw/ton * tons)
            fan_vent_kwh = fan_vent_run_hours_occ * fan_avg_vent_kw_per_ton * rtu.tons
            fan_clg_kwh = fan_clg_run_hours_occ * fan_avg_clg_kw_per_ton * rtu.tons
            fan_htg_kwh = fan_htg_run_hours_occ * fan_avg_htg_kw_per_ton * rtu.tons
            fan_kwh = fan_vent_kwh + fan_clg_kwh + fan_htg_kwh

            #final refrigeration kwh calc. Total expected runtime at efficiency, times tonnage, times kw/ton at avg condition
            refrig_kwh = eflh_c_occ_eff * refrig_kw_per_ton_at_oa_t * rtu.tons

            #totalize kwh from refrig, fan, and heating
            total_kwh = fan_kwh + refrig_kwh

            rtu.fan_vent_kwh_yearly = fan_vent_kwh
            rtu.fan_clg_kwh_yearly = fan_clg_kwh
            rtu.fan_htg_kwh_yearly = fan_htg_kwh
            rtu.fan_kwh_yearly = fan_kwh
            rtu.refrg_kwh_yearly = refrig_kwh
            rtu.kwh_hvac_yearly = total_kwh

            return total_kwh
        else:
            rtu.kwh_hvac_yearly = 0
            return 0