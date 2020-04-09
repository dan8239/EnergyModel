from Asset import *
from pyllist import dllist, dllistnode

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

    def add_ecm(self, ecm):
        self.ecm_list.appendright(ecm)

    def apply_ecms(self):
        for x in self.ecm_list.iternodes():
            if (x != None):
                x.value.apply_ecm(self.new_asset)
        
    def add_existing_asset(self, asset):
        if (not isinstance(asset, Asset)):
            raise TypeError("Cannot add a non Asset type to proposal existing asset: " + str(type(asset)))
        self.existing_asset = asset
        self.existing_asset.status = "existing"
        self.existing_asset.proposal = self

    def add_new_asset(self, asset):
        if (not isinstance(asset, Asset)):
            raise TypeError("Cannot add a non Asset type to proposal new asset: " + str(type(asset)))
        self.new_asset = asset
        self.new_asset.status = "new"
        self.new_asset.proposal = self


    def dump(self):
        if ((self.site == None) or (self.site == 0)):
            print("SiteID: " + str(self.site))
        else:
            print("SiteID: " + str(self.site.id))
        print("Proposal ID: " + str(self.prop_id))
        print("Existing Asset: ")
        if(self.existing_asset != None):
            self.existing_asset.dump()
        else:
            print("No Existing Asset")
        print("New Asset: ")
        if(self.new_asset != None):
            self.new_asset.dump()
        else:
            print("No New Asset")
        print("Strategy: " + str(self.strategy))
        print("New Asset: " + str(self.new_asset))
        print("-----------------------------------")