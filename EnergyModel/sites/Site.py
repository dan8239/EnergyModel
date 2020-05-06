from assets import Asset, Proposal, Cdu, Pkg
from pyllist import dllist, dllistnode
from weatherutility import geocode
from climdata import ClimateData
from energymodel import TddRtuModel
import pandas as pd

class Site:
    
    #constructor + instance variables
    def __init__(self, id):
        self.id = id
        self.portfolio = None
        self.address = None
        self.climate_data = ClimateData.ClimateData()
        self.latitude = None
        self.longitude = None
        self.altitude = None
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

    def geocode(self):
        if (self.address == None):
            raise TypeError("Address not instantiated. Cannot Geocode")
        else:
            locationobj = geocode.Geocode.geocode(self.address)
            self.latitude = locationobj.latitude
            self.longitude = locationobj.longitude
            self. altitude = locationobj.altitude

    def fill_climate_data(self):
        self.climate_data.get_closest_climate_zone(self.latitude, self.longitude)
        self.climate_data.calculate_climate_data()

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

    def to_dataframe(self):
        colnames = vars(self).keys()    #vars gets dict from object. Keys gets keys from dict key-value pairs
        df = pd.DataFrame([[getattr(self, j) for j in colnames]], columns = colnames) #get attributes in a row
        df['portfolio'] = self.portfolio.id    #take ID not whole object
        df['climate_data'] = self.climate_data.closest_climate_zone   #take city not whole object
        df = df.drop(['proposal_list',
                      'energy_model',
                      'altitude',
                      'pre_therms_hvac_yearly',
                      'post_therms_hvac_yearly',
                      'sav_therms_hvac_yearly'], axis = 1)   #drop object references
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
                
    def dump(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print()
        print("ID: " + str(self.id))
        print("address: " + str(self.address))
        print("latitude: " + str(self.latitude))
        print("longitude: " + str(self.longitude))
        print("altitude: " + str(self.altitude))
        print("Pre KWH: " + str(self.pre_kwh_hvac_yearly))
        print("Post KWH: " + str(self.post_kwh_hvac_yearly))
        print("Saved KWH: " + str(self.sav_kwh_hvac_yearly))
        if (self.climate_data != None):
            self.climate_data.dump()
        print("Total Assets:" + str(self.proposal_list.size))
        
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.dump()
        
        print()
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX END OF SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        
    def add_proposal(self, proposal):
        if (not isinstance(proposal, Proposal.Proposal)):
            raise TypeError("Cannot add a non Proposal type to site proposal_list")
        self.proposal_list.appendright(proposal)
        proposal.site = self