import pandas as pd
from portfolios import Portfolio
from sites import Site
from weatherutility import geocode
from assets import AssetFactory
import numpy as np

def __string_to_bool(string):
    if (string == True or string == "TRUE" or string == "True"):
        return True
    return False

def __replace_blank_with_0(input):
    if (input == np.nan or input == ""):
        return 0
    return input

#cleanse blanks and zeros to boolean values
def __cleanse_asset_list(asset_list):
    print("Cleansing Asset List")
    # Convert FALSE TRUE to Python Booleans
    asset_list['x_economizer'] = asset_list.apply(lambda x: __string_to_bool(x['x_economizer']),axis = 1)
    asset_list['x_vfd'] = asset_list.apply(lambda x: __string_to_bool(x['x_vfd']),axis = 1)
    asset_list['n_economizer'] = asset_list.apply(lambda x: __string_to_bool(x['n_economizer']),axis = 1)
    asset_list['n_vfd'] = asset_list.apply(lambda x: __string_to_bool(x['n_vfd']),axis = 1)
    #Convert string numbers to actual numbers
    pd.to_numeric(asset_list['x_tonnage'])
    pd.to_numeric(asset_list['n_tonnage'])
    pd.to_numeric(asset_list['x_eer'])
    pd.to_numeric(asset_list['n_eer'])
    pd.to_numeric(asset_list['x_cmp_stg'])
    pd.to_numeric(asset_list['n_cmp_stg'])
    pd.to_numeric(asset_list['x_evap_hp'])
    pd.to_numeric(asset_list['n_evap_hp'])
    #fill numeric blanks with 0
    asset_list.x_tonnage.fillna(value = 0, inplace = True)
    asset_list.x_evap_hp.fillna(value = 0, inplace = True)
    asset_list.x_eer.fillna(value = 0, inplace = True)
    asset_list.x_cmp_stg.fillna(value = 1, inplace = True)
    asset_list.n_tonnage.fillna(value = 0, inplace = True)
    asset_list.n_evap_hp.fillna(value = 0, inplace = True)
    asset_list.n_eer.fillna(value = 0, inplace = True)
    asset_list.n_cmp_stg.fillna(value = 1, inplace = True)


def __cleanse_site_list(site_list):
    print("Cleansing Site List")
    pd.to_numeric(site_list['latitude'])
    pd.to_numeric(site_list['longitude'])

def import_sites(import_filename, portfolio):
    print("Reading Site List")
    site_list = pd.read_csv(import_filename)
    __cleanse_site_list(site_list)
    for row in site_list.itertuples():
        site = Site.Site(row.site_id)
        site.address = row.address
        portfolio.add_site(site)
        if (row.latitude == np.nan or row.longitude == np.nan):
            print("Geocoding Site " + str(site.id))
            site.geocode()
        else:
            site.latitude = row.latitude
            site.longitude = row.longitude
        print("Filling Climate Data for Site " + str(site.id))
        site.fill_climate_data()


def import_assets(import_filename, portfolio):
    print("Reading Asset List")
    asset_list = pd.read_csv(import_filename)
    __cleanse_asset_list(asset_list)
    
    for row in asset_list.itertuples():
        #find correct site
        site = portfolio.find_site(row.site_id)
        print("Importing Asset for Site " + str(site.id))

        #create proposal and assets. Set Proposal values
        proposal = AssetFactory.AssetFactory.create_proposal(site,row.asset_type)
        proposal.prop_id = row.asset_id
        proposal.strategy = row.strategy

        #easier access to assets
        x_asset = proposal.existing_asset
        n_asset = proposal.new_asset

        #copy existing asset
        x_asset.copy_asset_from_row(row)
        n_asset.copy_asset_from_row(row)

        