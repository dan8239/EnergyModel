from sites import Site
from assets import Asset, Rtu, AssetFactory, Proposal
import datetime
from portfolios import Portfolio
from ecm import EnerfitVfd, RetroCommission
import pandas as pd
import numpy as np
from energymodel import TddRtuModel
from fileio import FileIO



def main():
    #create portfolio, add model type
    portfolio = Portfolio.Portfolio("LOWES_FULLSCHEDULE_70PCTMINFANSPD")
    

    #import sites from file, add to portfolio
    FileIO.import_sites("site_list_input.csv", portfolio)

    #read asset list
    FileIO.import_assets("asset_list_input.csv", portfolio)
    

    #for each asset listed
    #create proposal with existing and new asset
    #attach to appropriate site\

    #filter existing asset to fill data gaps
    portfolio.filter_assets()

    #apply ecms to each asset
    portfolio.apply_ecms()

    #run energy calculations pre and post
    portfolio.run_energy_calculations()

    #send to output files
    portfolio.portfolio_summary_table_to_csv(portfolio.id)
    portfolio.site_summary_table_to_csv(portfolio.id)
    portfolio.proposal_summary_table_to_csv(portfolio.id)
    #print("Printing Assets")
    #portfolio.dump()
    print("Pre-KWH: " + str(portfolio.pre_kwh_hvac_yearly))
    print("Post-KWH: " + str(portfolio.post_kwh_hvac_yearly))
    print("Sav-KWH: " + str(portfolio.sav_kwh_hvac_yearly))
    print("KWH Reduction %: " + str(portfolio.kwh_hvac_reduction_pct))


if __name__ == "__main__":
    main()
