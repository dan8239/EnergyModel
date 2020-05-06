import pandas as pd
from portfolios import Portfolio
from sites import Site
from weatherutility import geocode
from assets import AssetFactory
import numpy as np
from enumsets import FanSeq
import math
from openpyxl import load_workbook



def import_sites(filename, portfolio):
    print("Reading Site List")
    #site_list = pd.read_csv(import_filename)
    site_list = pd.read_excel(filename, sheet_name = "sites")
    __cleanse_site_list(site_list)
    for row in site_list.itertuples():
        site = Site.Site(row.site_id)
        site.address = row.address
        site.run_hours_yearly = 8760*row.occ_pcnt
        portfolio.add_site(site)
        if (row.latitude == np.nan or row.longitude == np.nan or math.isnan(row.latitude) or math.isnan(row.longitude)):
            print("Geocoding Site " + str(site.id))
            site.geocode()
            site_list.at[row.Index, 'latitude'] = site.latitude
            site_list.at[row.Index, 'longitude'] = site.longitude
            #row.longitude = site.longitude
        else:
            site.latitude = row.latitude
            site.longitude = row.longitude
        print("Filling Climate Data for Site " + str(site.id))
        site.fill_climate_data()

    #update input file to only pull lat/long once
    print("Updating Input File")
    #load existing workbook
    book = load_workbook(filename)
    #get writer for file, remove sites sheet
    writer = pd.ExcelWriter(filename, engine = 'openpyxl')
    writer.book = book
    std=book.get_sheet_by_name('sites')
    book.remove_sheet(std)
    #write updated sites sheet
    site_list.to_excel(writer, sheet_name = 'sites', index = False)
    #move back to first position
    book.move_sheet('sites',-1)
    writer.save()
    writer.close()
    #site_list.to_csv(import_filename, index = False)


def import_assets(filename, portfolio):
    print("Reading Asset List")
    asset_list = pd.read_excel(filename, sheet_name = "assets")
    #asset_list = pd.read_csv(filename)
    __cleanse_asset_list_df(asset_list)
    
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

#--------------------------------PRIVATE METHODS----------------------------------#

      
def __string_to_bool(string):
    if (string == True or string == "TRUE" or string == "True"):
        return True
    return False

def __replace_blank_with_0(input):
    if (input == np.nan or input == ""):
        return 0
    return input

def __fan_string_to_enum(input):
    val = None
    if (input == np.nan or 
        input == "" or 
        input == "CFD" or 
        input == "CONSTANT" or
        input == "Constant"):
        val = FanSeq.FanSeq.CONSTANT_SPEED
    elif (input == "STAGED" or 
          input == "Staged"):
        val = FanSeq.FanSeq.STAGED
    elif (input == "VARIABLE" or
          input == "VARIABLE AIRFLOW" or
          input == "VFD"):
        val = FanSeq.FanSeq.VARIABLE_AIRFLOW
    else:
        raise ImportError("Fan Sequence Type " + input + " unrecognized")
    return val

def __cleanse_econ_bool(asset_list_df):
    asset_list_df['x_economizer'] = asset_list_df.apply(lambda x: __string_to_bool(x['x_economizer']),axis = 1)
    asset_list_df['n_economizer'] = asset_list_df.apply(lambda x: __string_to_bool(x['n_economizer']),axis = 1)

def __cleanse_fan_bool(asset_list_df):
    asset_list_df['x_vfd'] = asset_list_df.apply(lambda x: __string_to_bool(x['x_vfd']),axis = 1)
    asset_list_df['n_vfd'] = asset_list_df.apply(lambda x: __string_to_bool(x['n_vfd']),axis = 1)

def __cleanse_fan_enum(asset_list_df):
    asset_list_df['x_fan_seq'] = asset_list_df.apply(lambda x: __fan_string_to_enum(x['x_fan_seq']),axis = 1)
    asset_list_df['n_fan_seq'] = asset_list_df.apply(lambda x: __fan_string_to_enum(x['n_fan_seq']),axis = 1)

def __cleanse_tonnage(asset_list_df):
    pd.to_numeric(asset_list_df['x_tonnage'])
    pd.to_numeric(asset_list_df['n_tonnage'])
    asset_list_df.x_tonnage.fillna(value = 0, inplace = True)
    asset_list_df.n_tonnage.fillna(value = 0, inplace = True)
    

def __cleanse_eer(asset_list_df):
    pd.to_numeric(asset_list_df['x_eer'])
    pd.to_numeric(asset_list_df['n_eer'])
    asset_list_df.x_eer.fillna(value = 0, inplace = True)
    asset_list_df.n_eer.fillna(value = 0, inplace = True)

def __cleanse_evap_hp(asset_list_df):
    pd.to_numeric(asset_list_df['x_evap_hp'])
    pd.to_numeric(asset_list_df['n_evap_hp'])
    asset_list_df.x_evap_hp.fillna(value = 0, inplace = True)
    asset_list_df.n_evap_hp.fillna(value = 0, inplace = True)

def __cleanse_x_cmp_stg(asset_list_df):
    pd.to_numeric(asset_list_df['x_cmp_stg'])
    pd.to_numeric(asset_list_df['n_cmp_stg'])
    asset_list_df.x_cmp_stg.fillna(value = 1, inplace = True)
    asset_list_df.n_cmp_stg.fillna(value = 1, inplace = True)

#cleanse blanks and zeros to boolean values
def __cleanse_asset_list_df(asset_list_df, inputversion = 2):

    print("Cleansing Asset List")
    # Convert FALSE TRUE to Python Booleans
    
    __cleanse_econ_bool(asset_list_df)
    if (inputversion == 1):
        __cleanse_fan_bool(asset_list_df)
    elif (inputversion == 2):
        __cleanse_fan_enum(asset_list_df)
    else:
        raise ImportError("Invalid input file version " + str(inputversion))


    asset_list_df.x_tonnage.fillna(value = 0, inplace = True)

    #Convert string numbers to actual numbers, fill blanks with 0
    __cleanse_tonnage(asset_list_df)
    __cleanse_eer(asset_list_df)
    __cleanse_evap_hp(asset_list_df)
    __cleanse_x_cmp_stg(asset_list_df)


def __cleanse_site_list(site_list):
    print("Cleansing Site List")
    pd.to_numeric(site_list['latitude'])
    pd.to_numeric(site_list['longitude'])