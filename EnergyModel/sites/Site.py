from assets import Asset, Proposal, Cdu, Pkg
from pyllist import dllist, dllistnode
from weatherutility import geocode
from climdata import LoadProfile
from energymodel import TddRtuModel
from utilitybills import EnergyBill
import pandas as pd
import numpy as np
from utility import Assumptions
from haversine import haversine, Unit

class Site:
    #constructor + instance variables
    def __init__(self, id):
        self.id = id
        self.portfolio = None
        self.address = None
        #self.occ_load_profile = LoadProfile.LoadProfile(type = "Occupied")
        #self.unocc_load_profile = LoadProfile.LoadProfile(type = "Unoccupied")
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.building_type = None
        self.closest_climate_city = None
        self.clg_design_temp = Assumptions.RtuDefaults.clg_design_temp
        self.htg_design_temp = Assumptions.RtuDefaults.htg_design_temp
        self.area = 0
        self.asset_count = 0
        self.run_hours_yearly = 8760
        self.x_tons = 0
        self.x_evap_hp = 0
        self.x_avg_age = 0
        self.x_avg_weighted_age = 0
        self.x_avg_eer = 0
        self.x_avg_weighted_eer = 0
        self.n_tons = 0
        self.n_evap_hp = 0
        self.n_avg_age = 0
        self.n_avg_weighted_age = 0
        self.n_avg_eer = 0
        self.n_avg_weighted_eer = 0
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        self.kwh_hvac_reduction_pct = 0
        self.proposal_list = dllist()
        self.energy_model = TddRtuModel.TddRtuModel()
        self.electric_bill = EnergyBill.ElectricBill(EnergyBill.BillDuration.YEARLY)
        self.electric_bill.site = self
        self.natural_gas_bill = EnergyBill.NaturalGasBill(EnergyBill.BillDuration.YEARLY)
        self.natural_gas_bill.site = self
        self.hvac_pcnt_of_electric_bill = 0
        self.total_kwh_reduction_pcnt = 0
    
    '''
    def fill_load_profile(self):
        self.occ_load_profile.get_closest_climate_city(self.latitude, self.longitude)
        self.occ_load_profile.calculate_load_profile()
    '''

    def fill_climate_info(self):
        (self.closest_climate_city, self.clg_design_temp, self.htg_design_temp) = self.__get_closest_climate_city()

    def run_energy_calculations(self, energy_model):
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.run_energy_calculations(energy_model)
        self.update_energy_totals()
   

    def filter_assets(self):
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.filter_assets()

    def apply_ecms(self):
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.attach_ecms()
                x.value.apply_ecms()

    def update_run_hours_yearly(self):
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.existing_asset.run_hours_yearly = self.run_hours_yearly
                x.value.new_asset.run_hours_yearly = self.run_hours_yearly

    def update_energy_totals(self):
        print("updating totals for site " + str(self.id))
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0

        self.asset_count = 0
        self.x_tons = 0
        self.x_evap_hp = 0
        x_age_tot = 0
        x_age_tons_tot = 0
        x_eer_tot = 0
        x_eer_tons_tot = 0
        self.n_tons = 0
        self.n_evap_hp = 0
        n_age_tot = 0
        n_age_tons_tot = 0
        n_eer_tot = 0
        n_eer_tons_tot = 0

        for x in self.proposal_list.iternodes():
            if (x !=None and (isinstance(x.value.existing_asset, Pkg.Pkg) or isinstance(x.value.existing_asset, Cdu.Cdu))):
                #existing asset sums
                self.asset_count = self.asset_count +1
                self.x_tons = self.x_tons + x.value.existing_asset.tons
                self.x_evap_hp = self.x_evap_hp + x.value.existing_asset.evap_hp
                x_age_tot = x_age_tot + x.value.existing_asset.age
                x_age_tons_tot = x_age_tons_tot + x.value.existing_asset.age * x.value.existing_asset.tons
                x_eer_tot = x_eer_tot + x.value.existing_asset.degr_eer
                x_eer_tons_tot = x_eer_tons_tot + x.value.existing_asset.degr_eer * x.value.existing_asset.tons

                #new asset sums
                self.n_tons = self.n_tons + x.value.new_asset.tons
                self.n_evap_hp = self.n_evap_hp + x.value.new_asset.evap_hp
                n_age_tot = n_age_tot + x.value.new_asset.age
                n_age_tons_tot = n_age_tons_tot + x.value.new_asset.age * x.value.new_asset.tons
                n_eer_tot = n_eer_tot + x.value.new_asset.degr_eer
                n_eer_tons_tot = n_eer_tons_tot + x.value.new_asset.degr_eer * x.value.new_asset.tons

                # energy calc sums
                self.pre_kwh_hvac_yearly = self.pre_kwh_hvac_yearly + x.value.pre_kwh_hvac_yearly
                self.post_kwh_hvac_yearly = self.post_kwh_hvac_yearly + x.value.post_kwh_hvac_yearly
                self.sav_kwh_hvac_yearly = self.sav_kwh_hvac_yearly + x.value.sav_kwh_hvac_yearly
                self.pre_therms_hvac_yearly = self.pre_therms_hvac_yearly + x.value.pre_therms_hvac_yearly
                self.post_therms_hvac_yearly = self.post_therms_hvac_yearly + x.value.post_therms_hvac_yearly
                self.sav_therms_hvac_yearly = self.sav_therms_hvac_yearly + x.value.sav_therms_hvac_yearly
        
        if (self.pre_kwh_hvac_yearly):
            self.kwh_hvac_reduction_pct = self.sav_kwh_hvac_yearly / self.pre_kwh_hvac_yearly
        else:
            self.kwh_hvac_reduction_pct = 0

        #asset avg metrics
        if (self.asset_count):
            self.x_avg_age = x_age_tot / self.asset_count
            self.x_avg_eer = x_eer_tot / self.asset_count
            self.n_avg_age = n_age_tot / self.asset_count
            self.n_avg_eer = n_eer_tot / self.asset_count
        else:
            self.x_avg_age = 0
            self.x_avg_eer = 0
            self.n_avg_age = 0
            self.n_avg_eer = 0
        if (self.x_tons):
            self.x_avg_weighted_age = x_age_tons_tot / self.x_tons
            self.x_avg_weighted_eer = x_eer_tons_tot / self.x_tons
            self.n_avg_weighted_age = n_age_tons_tot / self.n_tons
            self.n_avg_weighted_eer = n_eer_tons_tot / self.n_tons
        else:
            self.x_avg_weighted_age = 0
            self.x_avg_weighted_eer = 0
            self.n_avg_weighted_age = 0
            self.n_avg_weighted_eer = 0
        
        if (self.electric_bill.reliable):
            self.hvac_pcnt_of_electric_bill = self.pre_kwh_hvac_yearly / self.electric_bill.annual_units
            self.total_kwh_reduction_pcnt = self.sav_kwh_hvac_yearly / self.electric_bill.annual_units

    def to_dataframe(self):
        colnames = vars(self).keys()    #vars gets dict from object. Keys gets keys from dict key-value pairs
        df = pd.DataFrame([[getattr(self, j) for j in colnames]], columns = colnames) #get attributes in a row
        df['portfolio'] = self.portfolio.id    #take ID not whole object
        df = df.drop(['proposal_list',
                      'energy_model',
                      'altitude',
                      'x_avg_weighted_age',
                      'x_avg_weighted_eer',
                      'n_avg_weighted_age',
                      'n_avg_weighted_eer',
                      'pre_therms_hvac_yearly',
                      'post_therms_hvac_yearly',
                      'sav_therms_hvac_yearly',
                      'electric_bill',
                      'natural_gas_bill'], axis = 1)   #drop object references
        #merge utility bill information into dataframe
        elec_bill_df = self.electric_bill.to_dataframe()
        df = pd.merge(df, elec_bill_df, left_on='id', right_on='site', how='left').drop('site', axis = 1)
        return df

    def proposal_summary_table_dataframe(self):
        summary_df = pd.DataFrame()
        for x in self.proposal_list.iternodes():
            site_df = x.value.to_dataframe()
            if (summary_df.empty == True):
                summary_df = site_df
            else:
                summary_df = summary_df.append(site_df, ignore_index = True)
        return summary_df
                
        
    def add_proposal(self, proposal):
        if (not isinstance(proposal, Proposal.Proposal)):
            raise TypeError("Cannot add a non Proposal type to site proposal_list")
        self.proposal_list.appendright(proposal)
        proposal.site = self

    def geocode(self):
        if (self.address == None):
            raise TypeError("Address not instantiated. Cannot Geocode")
        else:
            locationobj = geocode.Geocode.geocode(self.address)
            self.latitude = locationobj.latitude
            self.longitude = locationobj.longitude
            self.altitude = locationobj.altitude     

# -------------------------- PRIVATE METHODS ------------------------#

    def __get_closest_climate_city(self):
        #check that lat/lon are good
        if (self.latitude == 0 or self.longitude == 0 or self.latitude == np.nan or self.longitude == np.nan):
            raise TypeError("Lat or Lon of 0 input to find closest weather data")

        #temp variables to check closest city
        input_city = (self.latitude, self.longitude)
        min_distance = float(99999999)
        temp_distance = float(99999999)
        closest_city = "No result"

        #create data frame from csv
        data = pd.read_csv('reference/CLIMATE-ZONE-LIST.csv')
        for i in data.index:
            
            temp_city = (pd.to_numeric(data['LAT'][i]), pd.to_numeric(data['LON'][i]))
            temp_distance = haversine(input_city, temp_city, unit=Unit.MILES)
            if (temp_distance < min_distance):
                min_distance = temp_distance
                closest_city = data['CLIMATE ZONE'][i]
                clg_design_tmp = data['DB DSGN TEMP C'][i]
                htg_design_tmp = data['DB DSGN TEMP H'][i]
                climate_zone = data['CLIMATE ZONE CODE'][i]
        self.climate_zone = climate_zone
        self.closest_climate_city = closest_city
        self.clg_design_temp = clg_design_tmp
        self.htg_design_temp = htg_design_tmp
        return closest_city, clg_design_tmp, htg_design_tmp



# ------------------------STATIC METHODS----------------------------#

def import_from_file(dataframe, portfolio):
    portfolio.update_input_file_flag = False
    for row in dataframe.itertuples():
        if (type(row.address) is str):
            #create site
            site = Site(row.site_id)
            #create import bill data
            site.electric_bill.import_from_row(row)
            #write all site values
            site.address = row.address
            site.run_hours_yearly = 8760*row.occ_pcnt
            site.area = row.area
            site.building_type = row.bldg_type
            portfolio.add_site(site)
            '''
            # grab balance temps if available
            if (np.isnan(row.occ_clg_balance_point_temp) or
                np.isnan(row.occ_htg_balance_point_temp)):
                dataframe.at[row.Index, 'occ_clg_balance_point_temp'] = site.occ_load_profile.clg_balance_point_temp
                dataframe.at[row.Index, 'occ_htg_balance_point_temp'] = site.occ_load_profile.htg_balance_point_temp
                portfolio.update_input_file_flag = True
            else:
                site.occ_load_profile.clg_balance_point_temp = row.occ_clg_balance_point_temp
                site.occ_load_profile.htg_balance_point_temp = row.occ_htg_balance_point_temp
            '''
            #geocode if lat/long is missing and write back into file
            if (np.isnan(row.latitude) or 
                np.isnan(row.longitude) or
                (row.latitude == 0 and row.longitude == 0)):
                print("Geocoding Site " + str(site.id))
                site.geocode()
                dataframe.at[row.Index, 'latitude'] = site.latitude
                dataframe.at[row.Index, 'longitude'] = site.longitude
                portfolio.update_input_file_flag = True
            else:
                site.latitude = row.latitude
                site.longitude = row.longitude
            #fill climate data for site
            #print("Filling Climate Data for Site " + str(site.id))
            #site.fill_load_profile()
            site.fill_climate_info()
        else:
            print("Site " + str(row.site_id) + " has no address listed. Will not be added to portfolio")
    #return dataframe for updating imput file    
    return dataframe
