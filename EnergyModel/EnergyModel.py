from portfolios import Portfolio
from ecm import VafEnerfit, RetroCommission, VafAutoClg, VafAutoVent, VafAutoHtg, SetpointAdj, FanStageClg, FanStageVent
from energymodel import TddRtuModel
from fileio import FileIO
from utility import Assumptions


def main():
    #create portfolio, add model type
    portfolio = Portfolio.Portfolio("LOWES-CONS")
    

    #import sites from file, add to portfolio
    input_filename = "projects/LOWES/input/input-CONS.xlsx"
    FileIO.import_sites(input_filename, portfolio)
    #read asset list
    FileIO.import_assets(input_filename, portfolio)

    #for each asset listed
    #create proposal with existing and new asset
    #attach to appropriate site\

    #filter existing asset to fill data gaps
    portfolio.filter_assets()

    '''
    #IRM Setup
    portfolio.add_ecm_list("Replace")
    portfolio.add_ecm_list("Retrofit-VFD")
    portfolio.add_ecm_list("Retrofit-Schedule")
    portfolio.add_ecm_list("No Action")
    portfolio.add_ecm("Retrofit-VFD",RetroCommission.RetroCommission(.30))
    portfolio.add_ecm("Retrofit-VFD",FanStageClg.FanStageClg())
    portfolio.add_ecm("Retrofit-VFD",FanStageVent.FanStageVent())
    portfolio.add_ecm("Retrofit-Schedule",SetpointAdj.SetpointAdj(new_occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp + 4))
    '''

    '''
    #BGHE Setup
    #attach ecms
    portfolio.add_ecm_list("Replace")
    portfolio.add_ecm_list("Retrofit")
    portfolio.add_ecm_list("No Action")
    portfolio.add_ecm("Retrofit",RetroCommission.RetroCommission())
    portfolio.add_ecm("Retrofit",VafEnerfit.VafEnerfit())
    portfolio.add_ecm("Replace",VafEnerfit.VafEnerfit())
    #portfolio.add_ecm("RETROFIT",SetpointAdj.SetpointAdj(new_occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp + 4))
    #portfolio.add_ecm("REPLACE",SetpointAdj.SetpointAdj(new_occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp + 4))
    '''
    
    #LOWES SETUP REGULAR
    #attach ecms
    portfolio.add_ecm_list("REPLACE")
    portfolio.add_ecm_list("RETROFIT")
    portfolio.add_ecm_list("NO ACTION")
    portfolio.add_ecm("RETROFIT",RetroCommission.RetroCommission())
    portfolio.add_ecm("RETROFIT",FanStageClg.FanStageClg())
    portfolio.add_ecm("RETROFIT",FanStageVent.FanStageVent())
    

    #apply ecms to each asset
    portfolio.apply_ecms()

    #run energy calculations pre and post
    portfolio.run_energy_calculations()

    #send to output files
    portfolio.to_excel_file()
    '''
    portfolio.portfolio_summary_table_to_csv(portfolio.id)
    portfolio.site_summary_table_to_csv(portfolio.id)
    portfolio.proposal_summary_table_to_csv(portfolio.id)
    '''
    print("Pre-KWH: " + str(portfolio.pre_kwh_hvac_yearly))
    print("Post-KWH: " + str(portfolio.post_kwh_hvac_yearly))
    print("Sav-KWH: " + str(portfolio.sav_kwh_hvac_yearly))
    print("KWH Reduction %: " + str(portfolio.kwh_hvac_reduction_pct))


if __name__ == "__main__":
    main()
