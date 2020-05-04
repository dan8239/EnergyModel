from ecm import Ecm
from assets import Rtu
from enumsets import FanSeq

class FanStageClg(Ecm.Ecm):
    def __init__(self, clg_fan_max_speed = 1.0, 
                 clg_fan_min_speed = 0.3333,
                 fan_stg = 2.0):
        self.clg_fan_min_speed = clg_fan_min_speed
        self.clg_fan_max_speed = clg_fan_max_speed
        self.fan_stg = fan_stg
        self.clg_fan_cntrl_seq = FanSeq.FanSeq.STAGED
        
    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            asset.fan_stg = self.fan_stg
            asset.clg_fan_cntrl_seq = self.clg_fan_cntrl_seq
            asset.clg_fan_max_speed = self.clg_fan_max_speed
            asset.clg_fan_min_speed = self.clg_fan_min_speed
            asset.clg_fan_cntrl_seq = self.clg_fan_cntrl_seq
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")
