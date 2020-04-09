from assets import pkg, ahu, cdu, asset

class AssetFactory():
    
    def create_proposal(site, type_of_asset):
        proposal = Proposal()
        site.add_proposal(proposal)
        if (type_of_asset == "Pkg" or type_of_asset == "Rtu" or type_of_asset == "PKG" or type_of_asset == "RTU"):
            x_asset = pkg.Pkg()
            n_asset = pkg.Pkg()
        elif (type_of_asset == "Ahu" or type_of_asset == "AHU"):
            x_asset = ahu.Ahu()
            n_asset = ahu.Ahu()
        elif (type_of_asset == "Cdu" or type_of_asset == "CDU"):
            x_asset = cdu.Cdu()
            n_asset = cdu.Cdu()
        elif (type_of_asset == "UH" or type_of_asset == "OTH"):
            x_asset = asset.Asset()
            n_asset = asset.Asset()
        else:
            raise TypeError("Invalid Asset Type Creation: " + str(type_of_asset))
        proposal.add_existing_asset(x_asset)
        proposal.add_new_asset(n_asset)
        return proposal


