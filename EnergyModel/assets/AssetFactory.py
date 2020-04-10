from assets import Asset, Pkg, Cdu, Ahu, Proposal

class AssetFactory():
    
    def create_proposal(site, type_of_asset):
        proposal = Proposal.Proposal()
        site.add_proposal(proposal)
        if (type_of_asset == "Pkg" or type_of_asset == "Rtu" or type_of_asset == "PKG" or type_of_asset == "RTU"):
            x_asset = Pkg.Pkg()
            n_asset = Pkg.Pkg()
        elif (type_of_asset == "Ahu" or type_of_asset == "AHU"):
            x_asset = Ahu.Ahu()
            n_asset = Ahu.Ahu()
        elif (type_of_asset == "Cdu" or type_of_asset == "CDU"):
            x_asset = Cdu.Cdu()
            n_asset = Cdu.Cdu()
        elif (type_of_asset == "UH" or type_of_asset == "OTH"):
            x_asset = Asset.Asset()
            n_asset = Asset.Asset()
        else:
            raise TypeError("Invalid Asset Type Creation: " + str(type_of_asset))
        proposal.add_existing_asset(x_asset)
        proposal.add_new_asset(n_asset)
        return proposal


