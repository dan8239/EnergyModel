from Site import *
from Asset import *
from Proposal import *
from Rtu import *
from AssetFactory import *

def main():
    site1 = Site(1)
    asset1 = AssetFactory.createAsset("Pkg")
    asset2 = AssetFactory.createAsset("Pkg")
    asset3 = AssetFactory.createAsset("Pkg")
    asset4 = AssetFactory.createAsset("Split")
    asset5 = AssetFactory.createAsset("Split")

    proposal1 = Proposal(site1, 1, asset1)
    proposal2 = Proposal(site1, 2, asset2)
    proposal3 = Proposal(site1, 3, asset3)
    proposal4 = Proposal(site1, 4, asset4)
    proposal5 = Proposal(site1, 5, asset5)

    site1.add_proposal(proposal1)
    site1.add_proposal(proposal2)
    site1.add_proposal(proposal3)
    site1.add_proposal(proposal4)
    site1.add_proposal(proposal5)

    for x in site1.proposal_list.iternodes():
            if (x != None):
                x.value.existing_asset.filter_asset()

    site1.print_all()

if __name__ == "__main__":
    main()
