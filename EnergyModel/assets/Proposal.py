from assets import Asset
from pyllist import dllist, dllistnode
import pandas as pd
from ecm import EnerfitVfd, RetroCommission, VfdAutoClg, VfdAutoHtg, VfdAutoVent

class Proposal:
    def __init__(self, site = None, prop_id = None, existing_asset = None, strategy = "No Action", new_asset = None):
        self.site = site
        self.prop_id = prop_id        
        self.strategy = strategy
        self.existing_asset = existing_asset
        if (self.existing_asset != None):
            self.existing_asset.proposal = self
        self.new_asset = new_asset
        self.ecm_list = dllist()
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        self.kwh_hvac_reduction_pct = 0

    def _add_ecm(self, ecm):
        self.ecm_list.appendright(ecm)

    def _apply_ecms(self):
        for x in self.ecm_list.iternodes():
            if (x != None):
                x.value.apply_ecm(self.new_asset)
        
    def add_existing_asset(self, asset):
        if (not isinstance(asset, Asset.Asset)):
            raise TypeError("Cannot add a non Asset type to proposal existing asset: " + str(type(asset)))
        self.existing_asset = asset
        self.existing_asset.status = "existing"
        self.existing_asset.proposal = self

    def add_new_asset(self, asset):
        if (not isinstance(asset, Asset.Asset)):
            raise TypeError("Cannot add a non Asset type to proposal new asset: " + str(type(asset)))
        self.new_asset = asset
        self.new_asset.status = "new"
        self.new_asset.proposal = self

    #filter old asset, if replacing filter new asset. If retro/no action copy old asset
    def filter_assets(self):
        print("Filter Assets for Proposal " + str(self.prop_id))
        self.existing_asset.filter_asset()
        if (self.strategy == "Replace" or self.strategy == "REPLACE"):
            self.new_asset.filter_asset()
        else:
            self.new_asset.copy_asset(self.existing_asset)

    def apply_ecms(self):
        # if retrofit, apply retrofit vfd actions to new asset
        print("Applying ECMs for Proposal " + str(self.prop_id))
        if (self.strategy == "Retrofit" or self.strategy == "RETROFIT"):
            self._add_ecm(RetroCommission.RetroCommission())
            self._add_ecm(VfdAutoClg.VfdAutoClg())
            self._add_ecm(VfdAutoVent.VfdAutoVent())
            self._apply_ecms()
        # if replace, set values from file and filter
        elif (self.strategy == "Replace" or self.strategy == "REPLACE"):
            if (self.new_asset.vfd == True):
                self._add_ecm(VfdAutoClg.VfdAutoClg())
                self._add_ecm(VfdAutoVent.VfdAutoVent())
            self._apply_ecms()

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
        column_names = ['site',
                        'asset_id',
                        'x_tons',
                        'x_hp',
                        'x_age',
                        'x_eer',
                        'x_vfd',
                        'strategy',
                        'n_tons',
                        'n_hp',
                        'n_age',
                        'n_eer',
                        'n_vfd',
                        'pre_kwh_hvac_yearly',
                        'post_kwh_hvac_yearly',
                        'sav_kwh_hvac_yearly',
                        'kwh_hvac_yearly_reduction_pct']
        values = [[self.site.id, 
                   self.prop_id, 
                   self.existing_asset.tons, 
                   self.existing_asset.evap_hp,
                   self.existing_asset.age,
                   self.existing_asset.degr_eer, 
                   self.existing_asset.vfd,
                   self.strategy,
                   self.new_asset.tons, 
                   self.new_asset.evap_hp,
                   self.new_asset.age,
                   self.new_asset.degr_eer, 
                   self.new_asset.vfd,
                   self.pre_kwh_hvac_yearly, 
                   self.post_kwh_hvac_yearly, 
                   self.sav_kwh_hvac_yearly,
                   self.kwh_hvac_reduction_pct]]
        return pd.DataFrame(values, columns=column_names)

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