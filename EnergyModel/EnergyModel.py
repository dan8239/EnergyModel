from Site import *
from Asset import *
from Proposal import *
from Rtu import *
from AssetFactory import *
from Portfolio import *
import pandas as pd

def main():
    site_list = pd.read_csv("site_list_input.csv")
    portfolio = Portfolio("test")

    for row in site_list.itertuples():
        site = Site(row.site_id)
        portfolio.add_site(site)

    asset_list = pd.read_csv("asset_list_input.csv")

    for row in asset_list.itertuples():
        site = portfolio.find_site(row.site_id)
        proposal = AssetFactory.create_proposal(site,row.asset_type)
        proposal.prop_id = row.asset_id
        asset = proposal.existing_asset
        if (isinstance(asset, Rtu)):
            asset.tons = row.tonnage
            asset.manufactured_year = row.year
            asset.calc_age()
            asset.econ = row.x_economizer
            asset.eer = row.x_eer
            asset.refrig_type = row.x_refrig_type
            asset.vfd = row.x_vfd
            asset.stg_cmp = row.x_cmp_stg
        asset.filter_asset()


    portfolio.dump()

    #site1 = Site(1)
    
    #AssetFactory.createAsset(site1, "Rtu")
    #AssetFactory.createAsset(site1, "Pkg")
    #AssetFactory.createAsset(site1, "Ahu")
    #AssetFactory.createAsset(site1, "Cdu")
    #AssetFactory.createAsset(site1, "Rtu")

    #for x in site1.proposal_list.iternodes():
    #        if (x != None):
    #            x.value.existing_asset.filter_asset()

    #site1.print_all()

if __name__ == "__main__":
    main()
