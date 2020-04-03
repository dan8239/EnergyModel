from Pkg import *
from Split import *

class AssetFactory():
    
    def createAsset(type_of_asset):
        if (type_of_asset == "Pkg"):
            asset = Pkg()
        elif (type_of_asset == "Split"):
            asset = Split()
        else:
            raise TypeError("Invalid Asset Type Creation")
        return asset


