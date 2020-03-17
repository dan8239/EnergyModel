from Asset import *
from pyllist import dllist, dllistnode
import pdb

class Site:

    #class variables
    compare_asset = Asset()
    
    #constructor + instance variables
    def __init__(self, id, asset_list = dllist()):
        self.id = id
        self.asset_list = asset_list
        self.asset_id_generator = 0
        
    def print_all(self):
        print("ID: " + str(self.id))
        print("Total Assets:" + str(self.asset_list.size))
        for x in self.asset_list.iternodes():
            if (x != None):
                x.value.print_all()
        print()
        
    def add_asset(self, asset):
        if (type(asset) != type(self.compare_asset)):
            raise TypeError("Cannot add a non Asset type to site asset_list")
        self.asset_list.appendright(asset)
        asset.site = self
        asset.auid = self.asset_id_generator
        self.asset_id_generator += 1
        
        
    def delete_asset_by_id(self, asset_id):
        for x in self.asset_list.iternodes():
            if (x.value.auid == asset_id):
                asset_list.remove(x)