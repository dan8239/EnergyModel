from ecm import Ecm
from assets import Rtu

class VfdAutoClg(Ecm.Ecm):
    def __init__(self, clg_fan_max_speed = 1.0, 
                 clg_fan_min_speed = 0.7, 
                 clg_fan_cntrl_seq = "VFD"):
        self.clg_fan_min_speed = clg_fan_min_speed
        self.clg_fan_max_speed = clg_fan_max_speed
        self.clg_fan_cntrl_seq = clg_fan_cntrl_seq
        
    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            asset.vfd = True
            asset.clg_fan_max_speed = self.clg_fan_max_speed
            asset.clg_fan_min_speed = self.clg_fan_min_speed
            asset.clg_fan_cntrl_seq = self.clg_fan_cntrl_seq
            
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")
