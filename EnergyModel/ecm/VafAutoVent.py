from ecm import Ecm
from assets import Rtu
from enumsets import FanSeq

class VafAutoVent(Ecm.Ecm):
    def __init__(self, vent_fan_max_speed = 1.0, 
                 vent_fan_min_speed = 0.333):
        self.vent_fan_min_speed = vent_fan_min_speed
        self.vent_fan_max_speed = vent_fan_max_speed
        self.vent_fan_cntrl_seq = FanSeq.FanSeq.VARIABLE_AIRFLOW
        
    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            asset.vent_fan_cntrl_seq = self.vent_fan_cntrl_seq
            asset.vent_fan_max_speed = self.vent_fan_max_speed
            asset.vent_fan_min_speed = self.vent_fan_min_speed
            asset.vent_fan_cntrl_seq = self.vent_fan_cntrl_seq
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")
