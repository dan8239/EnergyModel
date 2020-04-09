from Pkg import *
from Ahu import *
from Cdu import *
from Proposal import *

class AssetFactory():
    
    def create_proposal(site, type_of_asset):
        proposal = Proposal()
        site.add_proposal(proposal)
        if (type_of_asset == "Pkg" or type_of_asset == "Rtu" or type_of_asset == "PKG" or type_of_asset == "RTU"):
            x_asset = Pkg()
            n_asset = Pkg()
        elif (type_of_asset == "Ahu" or type_of_asset == "AHU"):
            x_asset = Ahu()
            n_asset = Ahu()
        elif (type_of_asset == "Cdu" or type_of_asset == "CDU"):
            x_asset = Cdu()
            n_asset = Cdu()
        elif (type_of_asset == "UH" or type_of_asset == "OTH"):
            x_asset = Asset()
            n_asset = Asset()
        else:
            raise TypeError("Invalid Asset Type Creation: " + str(type_of_asset))
        proposal.add_existing_asset(x_asset)
        proposal.add_new_asset(n_asset)
        return proposal


