from assets import Rtu, Cdu, Pkg

class TddRtuModel():
    """description of class"""
    def __init__(self):
        super().__init__()
        self.load_factor = 0.8
        self.kw_per_bhp = 0.7457
        self.max_cycling_degradation = 0.07
        self.fan_cube_law_factor = 3

    #based on efficiency curve. kw draw is 100% of peak at 95 deg F, 65.060241% at 65 deg F 
    def __refrig_kw_draw_pct_calc(self, rtu, oa_t):
        return 0.011646586*max(rtu.cmp_lockout_temp, oa_t) - 0.106435703

    #based on thermal output curve. Thermal output 100% at 95 deg F, 114% at 65 deg F
    def __refrig_therm_eff_pct_calc(self, rtu, oa_t):
        return -0.0046666667*max(rtu.cmp_lockout_temp, oa_t) + 1.44333333

    def __span(self, input, min, max):
        return (input * (max - min) + min)

    def __power_speed_ratio(self, rtu):   
        '''
        the average fan power calculated by averaging the 0-100% cooling load by hour is "speed"
        the average fan power calculated by averaging the 0-100% power draw by hour is "power"
        when the fan actually runs from a min to max value (i.e. not 0-100%), the result is skewed. 
        The closer to 100% range or span, power is more accurate. The closer to 0% range or span, the speed estimate is more accurate
        That ratio of power/speed estimate that accurately predicts actual fan draw from % loaded is the power_speed_ratio, and is variable by total span
        '''
        fan_span = rtu.clg_fan_max_speed - rtu.clg_fan_min_speed
        power_speed_ratio = 0.7568*(fan_span**2) + 0.1986*fan_span + 0.0192
        return power_speed_ratio

    def __avg_power_pct_blended(self, rtu, avg_power_pct_from_power, avg_power_pct_from_speed):
        #calc ratio from RTU min/max speeds
        pr = self.__power_speed_ratio(rtu)
        #blend fan power calcs appropriately
        avg_power_pct_blended = pr*avg_power_pct_from_power + (1-pr)*avg_power_pct_from_speed
        return avg_power_pct_blended

    def __vent_fan_speed(self, rtu):
        if rtu.vent_fan_cntrl_seq == "CFD":
            avg_vent_fan_speed = rtu.vent_fan_max_speed
        else:
            avg_vent_fan_speed = rtu.vent_fan_min_speed
        return avg_vent_fan_speed

    def __clg_fan_speed_stg_adj(self, rtu, fan_speed_pct):
        if (rtu.clg_fan_cntrl_seq == "CFD"):
            avg_clg_fan_speed = rtu.clg_fan_max_speed
        elif (rtu.clg_fan_cntrl_seq == "STAGED"):
            span = rtu.clg_fan_max_speed - rtu.clg_fan_min_speed
            #eq comes from stages having to operate in step fashion rather than vfd. Calculating rise/run
            avg_clg_fan_speed = span*(1 - 1/rtu.stg_cmp)*fan_speed_pct + span/rtu.stg_cmp + rtu.clg_fan_min_speed
        else:
            avg_clg_fan_speed = fan_speed_pct
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
            cd = rtu.climate_data

            #peak load calculations from EER, HP
            #break horsepower from list hp
            bhp = rtu.evap_hp * self.load_factor
            #peak fan kwh from bhp to kwh conversion
            fan_peak_kwh = bhp * self.kw_per_bhp / rtu.fan_efficiency
            #Peak fan kw/ton
            fan_peak_kw_per_ton = fan_peak_kwh / rtu.tons
            #peak RTU kw/ton from eer (total fan + refrigeration @ design)
            #note that the eer degradation is modeled to increase draw, but in reality just decreases thermal load
            rtu_peak_kw_per_ton = 12 / rtu.degr_eer
            #peak refrig kw/ton, total - fan
            refrig_peak_kw_per_ton = rtu_peak_kw_per_ton - fan_peak_kw_per_ton

            #Refrigeration efficiency adjustments at condition
            #refrig % of peak draw at entering air conditions
            refrig_kw_draw_pct_at_oa_t = self.__refrig_kw_draw_pct_calc(rtu, cd.avg_clg_oa_t)
            #refrig efficiency gain at entering air conditions
            refrig_eff_pct_at_oa_t = self.__refrig_therm_eff_pct_calc(rtu, cd.avg_clg_oa_t)
            #peak thermal load percentage taking design factor into account
            refrig_peak_therm_load_pct = 1 / (1 + rtu.clg_design_factor)
            #thermal load percentage at avg condition, adding in efficiency gain of refrigeration
            ### Use For Fan Calcs###
            refrig_therm_load_pct_at_oa_t = refrig_peak_therm_load_pct / refrig_eff_pct_at_oa_t * cd.avg_clg_load_pct
            #cycling on low load kw draw penalty. Divide penalty by number of compressors
            refrig_kw_draw_pct_cycling_penalty = 1 + (1-refrig_therm_load_pct_at_oa_t) * self.max_cycling_degradation / rtu.stg_cmp
            #total refrigeration draw when running at condition
            refrig_kw_per_ton_at_oa_t = refrig_peak_kw_per_ton * refrig_kw_draw_pct_at_oa_t * refrig_kw_draw_pct_cycling_penalty

            #occ hours calculations
            #refrigeration runtime raw
            eflh_c_occ = cd.eflh_c * rtu.run_hours_yearly / 8760
            #reduce refrigeration hours for thermal efficiency increase
            eflh_c_occ_eff = eflh_c_occ / refrig_eff_pct_at_oa_t
            #fan heating run hours
            fan_htg_run_hours = cd.htg_hrs * cd.avg_htg_load_pct
            fan_htg_run_hours_occ = fan_htg_run_hours * rtu.run_hours_yearly / 8760
            #fan cooling run hours
            fan_clg_run_hours = cd.clg_hrs * cd.avg_clg_load_pct
            fan_clg_run_hours_occ = fan_clg_run_hours * rtu.run_hours_yearly / 8760
            #vent run hours
            fan_vent_run_hours = 8760 - fan_htg_run_hours - fan_clg_run_hours
            fan_vent_run_hours_occ = fan_vent_run_hours * rtu.run_hours_yearly / 8760

            #calc avg power (speed method)
            #step 1 reduce avg speed % for design margin and efficiency gain
            fan_clg_avg_speed_pct_from_speed_therm_redux = cd.avg_clg_fan_speed_pct_from_speed * refrig_peak_therm_load_pct / refrig_eff_pct_at_oa_t
            #step 2 span avg speed % for actual RTU min/max speeds
            fan_clg_avg_speed_pct_from_speed_span = self.__span(fan_clg_avg_speed_pct_from_speed_therm_redux, rtu.clg_fan_min_speed, rtu.clg_fan_max_speed)
            #step 3 adjust avg speed % if fan is staged or cfd
            fan_clg_avg_speed_pct_from_speed_final = self.__clg_fan_speed_stg_adj(rtu, fan_clg_avg_speed_pct_from_speed_span)
            #step 4 convert avg speed to avg power
            fan_clg_avg_power_pct_from_speed = fan_clg_avg_speed_pct_from_speed_final**self.fan_cube_law_factor

            #calc avg power (power method)
            #step 1 reduce avg speed % for design margin and efficiency gain
            fan_clg_avg_speed_pct_from_power_therm_redux = cd.avg_clg_fan_speed_pct_from_power * refrig_peak_therm_load_pct / refrig_eff_pct_at_oa_t
            #step 2 span avg speed % for actual RTU min/max speeds
            fan_clg_avg_speed_pct_from_power_span = self.__span(fan_clg_avg_speed_pct_from_power_therm_redux, rtu.clg_fan_min_speed, rtu.clg_fan_max_speed)
            #step 3 adjust avg speed % if fan is staged or cfd
            fan_clg_avg_speed_pct_from_power_final = self.__clg_fan_speed_stg_adj(rtu, fan_clg_avg_speed_pct_from_power_span)
            #step 4 convert avg speed to avg power
            fan_clg_avg_power_pct_from_power = fan_clg_avg_speed_pct_from_power_final**self.fan_cube_law_factor
            
            #calc avg power pct blended
            fan_clg_avg_power_pct_blended = self.__avg_power_pct_blended(rtu, fan_clg_avg_power_pct_from_power, fan_clg_avg_power_pct_from_speed)
            fan_avg_clg_kw_per_ton = fan_peak_kw_per_ton * fan_clg_avg_power_pct_blended

            #fan speed calculations
            fan_avg_vent_speed = self.__vent_fan_speed(rtu)
            #fan_avg_clg_speed = self.__clg_fan_speed(rtu, refrig_therm_load_pct_at_oa_t)
            fan_avg_htg_speed = self.__htg_fan_speed(rtu, cd.avg_htg_load_pct)
            #fan kw/ton calculations (fan cube law)
            fan_avg_vent_kw_per_ton = fan_peak_kw_per_ton * fan_avg_vent_speed ** self.fan_cube_law_factor
            #fan_avg_clg_kw_per_ton = fan_peak_kw_per_ton * fan_avg_clg_speed ** self.fan_cube_law_factor
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