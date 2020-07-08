from ecm import Ecm
from assets import Rtu
from utility import Assumptions

class SetpointAdj(Ecm.Ecm):
    def __init__(self, new_occ_htg_sp = Assumptions.RtuDefaults.occ_htg_sp, new_occ_clg_sp = Assumptions.RtuDefaults.occ_clg_sp):
        self.new_occ_htg_sp = new_occ_htg_sp
        self.new_occ_clg_sp = new_occ_clg_sp
        
    
    def __design_factor_to_load_at_design(self, design_factor):
        return (1/(1 + design_factor))

    def __load_at_design_to_design_factor(self, load_at_design):
        return (1/load_at_design - 1)

    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            # get full design load at existing swing temperature
            clg_load_at_design = self.__design_factor_to_load_at_design(asset.clg_design_factor)
            htg_load_at_design = self.__design_factor_to_load_at_design(asset.htg_design_factor)

            #get new swing temperatures based on delta T
            clg_delta_t = self.new_occ_clg_sp - asset.occ_clg_sp
            htg_delta_t = self.new_occ_htg_sp - asset.occ_htg_sp
            new_clg_balance_point_temp = asset.occ_load_profile.clg_balance_point_temp + clg_delta_t
            new_htg_balance_point_temp = asset.occ_load_profile.htg_balance_point_temp + htg_delta_t

            # get new clg design factor based on new swing temperatures
            clg_design_adj_fact = (asset.occ_load_profile.clg_design_temp - new_clg_balance_point_temp) / (asset.occ_load_profile.clg_design_temp - asset.occ_load_profile.clg_balance_point_temp)
            new_clg_load_at_design = clg_load_at_design * clg_design_adj_fact
            new_clg_design_factor = self.__load_at_design_to_design_factor(new_clg_load_at_design)
            asset.clg_design_factor = new_clg_design_factor

            # get new htg design factor based on new swing temperatures
            htg_design_adj_fact = (asset.occ_load_profile.htg_design_temp - new_htg_balance_point_temp) / (asset.occ_load_profile.htg_design_temp - asset.occ_load_profile.htg_balance_point_temp)
            new_htg_load_at_design = htg_load_at_design * htg_design_adj_fact
            new_htg_design_factor = self.__load_at_design_to_design_factor(new_htg_load_at_design)
            asset.htg_design_factor = new_htg_design_factor

            asset.update_load_profile(new_htg_balance_point_temp, new_clg_balance_point_temp)
            
            
        else:
            #raise NotImplementedError("ECM Type not supported for Asset Type")
            pass
