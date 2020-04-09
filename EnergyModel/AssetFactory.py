from Pkg import *
from Ahu import *
from Cdu import *
from Proposal import *

class AssetFactory():
    
    def create_proposal(site, type_of_asset):
        proposal = Proposal()
        site.add_proposal(proposal)
        if (type_of_asset == "Pkg" or type_of_asset == "Rtu" or type_of_asset == "PKG" or type_of_asset == "RTU"):
            asset = Pkg()
        elif (type_of_asset == "Ahu" or type_of_asset == "AHU"):
            asset = Ahu()
        elif (type_of_asset == "Cdu" or type_of_asset == "CDU"):
            asset = Cdu()
        elif (type_of_asset == "UH" or type_of_asset == "OTH"):
            asset = Asset()
        else:
            raise TypeError("Invalid Asset Type Creation: " + str(type_of_asset))
        proposal.add_existing_asset(asset)
        return proposal


