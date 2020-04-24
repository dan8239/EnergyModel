from ecm import Ecm
from assets import Rtu

class VfdAutoHtg(Ecm.Ecm):
    def __init__(self, htg_fan_max_speed = 1.0, 
                 htg_fan_min_speed = 0.4,
                 htg_fan_cntrl_seq = "VFD"):
        self.htg_fan_min_speed = htg_fan_min_speed
        self.htg_fan_max_speed = htg_fan_max_speed
        self.htg_fan_cntrl_seq = htg_fan_cntrl_seq

    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            asset.vfd = True
            asset.htg_fan_max_speed = self.htg_fan_max_speed
            asset.htg_fan_min_speed = self.htg_fan_min_speed
            asset.htg_fan_cntrl_seq = self.htg_fan_cntrl_seq

        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")
