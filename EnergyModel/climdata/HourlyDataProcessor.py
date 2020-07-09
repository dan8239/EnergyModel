import datetime
import pandas as pd

def __add_datetime(dataframe):
    copy = dataframe.drop(columns=["HR OF YR","DRY BULB","WET BULB"])
    #dataframe as string, concatenate columns to string and add datetime column)
    dataframe["DATETIME"] = pd.to_datetime(copy.astype(str).apply(lambda x: "2020-"+x['MON']+"-"+x['DAY']+" "+x["HR"]+":00", axis=1))
    return dataframe

def add_dow(dataframe):
    change = False
    if "DATETIME" not in dataframe.columns:
        dataframe = __add_datetime(dataframe)
        change = True
    if "DOW" not in dataframe.columns:
        dataframe = dataframe.assign(DOW=dataframe['DATETIME'].dt.dayofweek)
        change = True
    dataframe.drop(dataframe.columns[dataframe.columns.str.contains('unnamed', case = False)], axis = 1, inplace = True)
    return dataframe, change

def append_occ(dataframe, weekday_start_time, weekday_stop_time, weekend_start_time, weekend_stop_time):
    #day of week matches and hour >= start and < stop
    mask = ((dataframe['DOW'] <= 4) & ((dataframe['HR'] >= weekday_start_time) & (dataframe['HR'] < weekday_stop_time)) | ((dataframe['DOW'] > 4) & ((dataframe['HR'] >= weekend_start_time) & (dataframe['HR'] < weekend_stop_time))))
    dataframe = dataframe.assign(OCC=mask)
    return dataframe
    

def append_hourly_calcs(dataframe, clg_balance_point_temp, htg_balance_point_temp, clg_design_temp, htg_design_temp):
    dataframe['CDD'] = __calc_hourly_cdd(dataframe['DRY BULB'].values, clg_balance_point_temp)
    dataframe['HDD'] = __calc_hourly_hdd(dataframe['DRY BULB'].values, htg_balance_point_temp)
    dataframe['EFLH-C'] = __calc_hourly_eflh_c(dataframe['CDD'].values, clg_design_temp, clg_balance_point_temp)
    dataframe['EFLH-H'] = __calc_hourly_eflh_h(dataframe['HDD'].values, htg_design_temp, htg_balance_point_temp)
    dataframe['EFLH-T'] = __calc_hourly_eflh_t(dataframe['EFLH-C'].values, dataframe['EFLH-H'].values)
    dataframe['CLG-HRS'] = __calc_clg_hr(dataframe['DRY BULB'].values, clg_balance_point_temp)
    dataframe['HTG-HRS'] = __calc_htg_hr(dataframe['DRY BULB'].values, htg_balance_point_temp)
    dataframe['VENT-HRS'] = __calc_vent_hr(dataframe['CLG-HRS'].values, dataframe['HTG-HRS'].values)
    dataframe['CLG-FAN-PWR-%'] = __cubed(dataframe['EFLH-C'].values)
    dataframe['HTG-FAN-PWR-%'] = __cubed(dataframe['EFLH-H'].values)
    return dataframe


def __calc_hourly_cdd(temp, balance_point_temp):
    calc = temp - balance_point_temp
    sign = (calc > 0)*1
    val = calc * sign / 24
    return val

def __calc_hourly_hdd(temp, balance_point_temp):
    calc = balance_point_temp - temp
    sign = (calc > 0)*1
    val = calc * sign / 24
    return val

def __calc_hourly_eflh_c(cdd, design_temp, balance_point_temp):
    return cdd*24/(design_temp - balance_point_temp)

def __calc_hourly_eflh_h(hdd, design_temp, balance_point_temp):
    return hdd*24/(balance_point_temp - design_temp)

def __calc_hourly_eflh_t(eflh_c, eflh_h):
    return eflh_c + eflh_h

def __calc_clg_hr(temp, balance_point_temp):
    calc = ((temp - balance_point_temp) > 0)
    #convert to int
    return calc*1

def __calc_htg_hr(temp, balance_point_temp):
    calc = ((balance_point_temp - temp) > 0)
    #convert to int
    return calc*1

def __calc_vent_hr(htg_flag, clg_flag):
    calc = (htg_flag + clg_flag == 0)
    return calc

def __cubed(prcnt):
    return prcnt**3

def __span(input, min, max, filter):
    return (input*(max - min) + min) * filter
