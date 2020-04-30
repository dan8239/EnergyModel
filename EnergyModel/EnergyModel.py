from portfolios import Portfolio
from ecm import EnerfitVfd, RetroCommission, VfdAutoClg, VfdAutoVent, VfdAutoHtg, SetpointAdj
from energymodel import TddRtuModel
from fileio import FileIO
from utility import Assumptions


def main():
    #create portfolio, add model type
    portfolio = Portfolio.Portfolio("LOWES_TEST")
    

    #import sites from file, add to portfolio
    FileIO.import_sites("site_list_input_LOWES_SHORT.csv", portfolio)

    #read asset list
    FileIO.import_assets("asset_list_input_LOWES_SHORT.csv", portfolio)
    

    #for each asset listed
    #create proposal with existing and new asset
    #attach to appropriate site\

    #filter existing asset to fill data gaps
    portfolio.filter_assets()


    #attach ecms
    portfolio.add_ecm_list("REPLACE")
    portfolio.add_ecm_list("RETROFIT")
    portfolio.add_ecm_list("NO ACTION")
    portfolio.add_ecm("RETROFIT",RetroCommission.RetroCommission())
    portfolio.add_ecm("RETROFIT",VfdAutoClg.VfdAutoClg(clg_fan_min_speed = 0.7))
    portfolio.add_ecm("RETROFIT",VfdAutoVent.VfdAutoVent(vent_fan_min_speed = 0.7))
    portfolio.add_ecm("RETROFIT",SetpointAdj.SetpointAdj(new_occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp + 4))
    portfolio.add_ecm("REPLACE",SetpointAdj.SetpointAdj(new_occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp + 4))

    #apply ecms to each asset
    portfolio.apply_ecms()

    #run energy calculations pre and post
    portfolio.run_energy_calculations()

    #send to output files
    #portfolio.portfolio_summary_table_to_csv(portfolio.id)
    #portfolio.site_summary_table_to_csv(portfolio.id)
    #portfolio.proposal_summary_table_to_csv(portfolio.id)
    #print("Printing Assets")
    #portfolio.dump()
    print("Pre-KWH: " + str(portfolio.pre_kwh_hvac_yearly))
    print("Post-KWH: " + str(portfolio.post_kwh_hvac_yearly))
    print("Sav-KWH: " + str(portfolio.sav_kwh_hvac_yearly))
    print("KWH Reduction %: " + str(portfolio.kwh_hvac_reduction_pct))
    portfolio.avg_power_speed_ratio()


if __name__ == "__main__":
    main()
