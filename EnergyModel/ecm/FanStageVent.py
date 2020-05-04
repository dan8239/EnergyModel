from ecm import Ecm
from assets import Rtu
from enumsets import FanSeq

class FanStageVent(Ecm.Ecm):
    def __init__(self, vent_fan_max_speed = 1.0, 
                 vent_fan_min_speed = 0.3333,
                 fan_stg = 2.0):
        self.vent_fan_min_speed = vent_fan_min_speed
        self.vent_fan_max_speed = vent_fan_max_speed
        self.fan_stg = fan_stg
        self.vent_fan_cntrl_seq = FanSeq.FanSeq.STAGED
        
    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            asset.fan_stg = self.fan_stg
            asset.vent_fan_cntrl_seq = self.vent_fan_cntrl_seq
            asset.vent_fan_max_speed = self.vent_fan_max_speed
            asset.vent_fan_min_speed = self.vent_fan_min_speed
            asset.vent_fan_cntrl_seq = self.vent_fan_cntrl_seq
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")
