from assets import Asset
from pyllist import dllist, dllistnode
import pandas as pd
from climdata import HourlyDataManager

class Proposal:
    def __init__(self, site = None, prop_id = None, existing_asset = None, strategy = "No Action", new_asset = None):
        self.site = site
        self.prop_id = prop_id        
        self.strategy = strategy
        self.existing_asset = existing_asset
        if (self.existing_asset != None):
            self.existing_asset.proposal = self
        self.new_asset = new_asset
        self.ecm_list = None
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        self.kwh_hvac_reduction_pct = 0
       
    #add asset to proposal, set all connections and get hourly data
    def add_existing_asset(self, asset):
        if (not isinstance(asset, Asset.Asset)):
            raise TypeError("Cannot add a non Asset type to proposal existing asset: " + str(type(asset)))
        self.existing_asset = asset
        self.existing_asset.status = "existing"
        self.existing_asset.proposal = self
        self.existing_asset.hourly_data = HourlyDataManager.HourlyDataManager.get_hourly_data(self.existing_asset)

    #add asset to proposal, set all connections and get hourly data
    def add_new_asset(self, asset):
        if (not isinstance(asset, Asset.Asset)):
            raise TypeError("Cannot add a non Asset type to proposal new asset: " + str(type(asset)))
        self.new_asset = asset
        self.new_asset.status = "new"
        self.new_asset.proposal = self
        self.new_asset.hourly_data = HourlyDataManager.HourlyDataManager.get_hourly_data(self.new_asset)

    #filter old asset, if replacing filter new asset. If retro/no action copy old asset
    def filter_assets(self):
        print("Filter Assets for Proposal " + str(self.prop_id))
        self.existing_asset.filter_asset()
        if (self.strategy == "Replace" or self.strategy == "REPLACE"):
            self.new_asset.filter_asset()
        else:
            self.new_asset.copy_asset(self.existing_asset)

    def attach_ecms(self):
        self.ecm_list = self.site.portfolio.get_ecm_list(self.strategy)
    
    def apply_ecms(self):
        self.ecm_list.apply_ecms(self.new_asset)

    def run_energy_calculations(self, energy_model):
        self.existing_asset.run_energy_calculations(energy_model)
        self.new_asset.run_energy_calculations(energy_model)
        self.__update_energy_totals()
        
    
    def __update_energy_totals(self):
        self.pre_kwh_hvac_yearly = self.existing_asset.kwh_hvac_yearly
        self.post_kwh_hvac_yearly = self.new_asset.kwh_hvac_yearly
        self.sav_kwh_hvac_yearly = self.pre_kwh_hvac_yearly - self.post_kwh_hvac_yearly
        self.pre_therms_hvac_yearly = self.existing_asset.therms_hvac_yearly
        self.post_therms_hvac_yearly = self.new_asset.therms_hvac_yearly
        self.sav_therms_hvac_yearly = self.pre_therms_hvac_yearly - self.post_therms_hvac_yearly
        if (self.pre_kwh_hvac_yearly):
            self.kwh_hvac_reduction_pct = self.sav_kwh_hvac_yearly / self.pre_kwh_hvac_yearly
        else:
            self.kwh_hvac_reduction_pct = 0

    def to_dataframe(self):
        colnames = vars(self).keys()    #vars gets dict from object. Keys gets keys from dict key-value pairs
        df = pd.DataFrame([[getattr(self, j) for j in colnames]], columns = colnames) #get attributes in a row
        df['site'] = self.site.id    #take site ID not whole object
        df.insert(2, 'asset_type', self.existing_asset.__class__.__name__)
        df = df.drop(['existing_asset',
                      'new_asset','ecm_list',
                      'pre_therms_hvac_yearly',
                      'post_therms_hvac_yearly',
                      'sav_therms_hvac_yearly'], axis = 1)   #drop object references
        return df

    def dump(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX PROPOSAL OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        if ((self.site == None) or (self.site == 0)):
            print("SiteID: " + str(self.site))
        else:
            print("SiteID: " + str(self.site.id))
        print("Proposal ID: " + str(self.prop_id))
        print("Strategy: " + str(self.strategy))
        print("Pre KWH: " + str(self.pre_kwh_hvac_yearly))
        print("Post KWH: " + str(self.post_kwh_hvac_yearly))
        print("Saved KWH: " + str(self.sav_kwh_hvac_yearly))
        print("Existing Asset: ")
        if(self.existing_asset != None):
            self.existing_asset.dump()
        else:
            print("No Existing Asset")
        print("<><><>><><><><><><><><><><><><><><>")
        print("New Asset: ")
        if(self.new_asset != None):
            self.new_asset.dump()
        else:
            print("No New Asset")
        print("Strategy: " + str(self.strategy))
        print("New Asset: " + str(self.new_asset))
        print("-----------------------------------")