from ecm import Ecm
from assets import Rtu
from enumsets import FanSeq

class VafEnerfit(Ecm.Ecm):
    def __init__(self, clg_fan_max_speed = 1.0, 
                 clg_fan_min_speed = 0.25, 
                 htg_fan_max_speed = 0.8, 
                 htg_fan_min_speed = 0.8, 
                 vent_fan_max_speed = 1.0, 
                 vent_fan_min_speed = 0.25,
                 clg_fan_cntrl_seq = FanSeq.FanSeq.VARIABLE_AIRFLOW,
                 htg_fan_cntrl_seq = FanSeq.FanSeq.VARIABLE_AIRFLOW,
                 vent_fan_cntrl_seq = FanSeq.FanSeq.VARIABLE_AIRFLOW):
        self.vent_fan_min_speed = vent_fan_min_speed
        self.vent_fan_max_speed = vent_fan_max_speed
        self.vent_fan_cntrl_seq = vent_fan_cntrl_seq

        self.clg_fan_min_speed = clg_fan_min_speed
        self.clg_fan_max_speed = clg_fan_max_speed
        self.clg_fan_cntrl_seq = clg_fan_cntrl_seq

        self.htg_fan_min_speed = htg_fan_min_speed
        self.htg_fan_max_speed = htg_fan_max_speed
        self.htg_fan_cntrl_seq = htg_fan_cntrl_seq
        

    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            asset.htg_fan_max_speed = self.htg_fan_max_speed
            asset.htg_fan_min_speed = self.htg_fan_min_speed
            asset.htg_fan_cntrl_seq = self.htg_fan_cntrl_seq

            asset.clg_fan_max_speed = self.clg_fan_max_speed
            asset.clg_fan_min_speed = self.clg_fan_min_speed
            asset.clg_fan_cntrl_seq = self.clg_fan_cntrl_seq
            
            asset.vent_fan_max_speed = self.vent_fan_max_speed
            asset.vent_fan_min_speed = self.vent_fan_min_speed
            asset.vent_fan_cntrl_seq = self.vent_fan_cntrl_seq
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")