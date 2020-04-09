import Site
from assets import Asset
from Proposal import *
import Rtu
import datetime
from AssetFactory import *
from Portfolio import *
from RetrofitVfd import *
import pandas as pd
import numpy as np

def __string_to_bool(string):
    if (string == "TRUE" or string == "True"):
        return True
    return False

def main():
    #read site list and create portfolio with list of sites attached
    
    print("Reading Site List")
    site_list = pd.read_csv("site_list_input.csv")
    portfolio = Portfolio("test")

    for row in site_list.itertuples():
        site = Site.Site(row.site_id)
        portfolio.add_site(site)

    #read asset list
    print("Reading Asset List")
    asset_list = pd.read_csv("asset_list_input.csv")

    #cleanse blanks and zeros to boolean values
    print("Cleansing Asset List")
    asset_list['x_economizer'] = asset_list.apply(lambda x: __string_to_bool(x['x_economizer']),axis = 1)
    asset_list['x_vfd'] = asset_list.apply(lambda x: __string_to_bool(x['x_vfd']),axis = 1)
    asset_list['x_cmp_stg'] = asset_list.apply(lambda x: __string_to_bool(x['x_cmp_stg']),axis = 1)
    asset_list['n_economizer'] = asset_list.apply(lambda x: __string_to_bool(x['n_economizer']),axis = 1)
    asset_list['n_vfd'] = asset_list.apply(lambda x: __string_to_bool(x['n_vfd']),axis = 1)
    asset_list['n_cmp_stg'] = asset_list.apply(lambda x: __string_to_bool(x['n_cmp_stg']),axis = 1)

    #for each asset listed
    #create proposal with existing and new asset
    #attach to appropriate site
    print("Importing Assets")
    for row in asset_list.itertuples():
        #find correct site
        site = portfolio.find_site(row.site_id)

        #create proposal and assets. Set Prop values
        proposal = AssetFactory.create_proposal(site,row.asset_type)
        proposal.prop_id = row.asset_id
        proposal.strategy = row.strategy
        x_asset = proposal.existing_asset
        n_asset = proposal.new_asset

        #for RTU's set all values appropriately
        if (isinstance(x_asset, Rtu.Rtu)):
            x_asset.tons = row.x_tonnage
            x_asset.manufactured_year = row.year
            x_asset.calc_age()
            x_asset.econ = row.x_economizer
            x_asset.eer = row.x_eer
            x_asset.refrig_type = row.x_refrig_type
            x_asset.vfd = row.x_vfd
            x_asset.stg_cmp = row.x_cmp_stg

            #cleanse data gaps with actionable knowledge
            x_asset.filter_asset()

            # if not replacing, new asset takes old asset info
            if (proposal.strategy != "Replace"):
                n_asset.copy_asset(x_asset)
            # if retrofit, apply retrofit vfd actions to new asset
            if (proposal.strategy == "Retrofit"):
                proposal.add_ecm = RetrofitVfd()
                proposal.apply_ecms()
            # if replace, set values from file and filter
            elif (proposal.strategy == "Replace"):
                n_asset.tons = row.n_tonnage
                n_asset.manufactured_year = datetime.datetime.now().year
                n_asset.calc_age()
                n_asset.econ = row.n_economizer
                n_asset.eer = row.n_eer
                n_asset.vfd = row.n_vfd
                n_asset.stg_cmp = row.n_cmp_stg
                n_asset.filter_asset()
    print("Printing Assets")
    portfolio.dump()


if __name__ == "__main__":
    main()
