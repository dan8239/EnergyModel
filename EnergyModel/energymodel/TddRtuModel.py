from energymodel import RtuModel
from assets import Rtu

class TddRtuModel(RtuModel):
    """description of class"""
    def __init__(self):
        super().__init__()
        self.load_factor = 0.8
        self.kw_per_bhp = 0.7457
        self.fan_efficiency = 0.85
        self.clg_design_factor = 0.2
        self.htg_design_factor = 0.4
        self.vent_fan_speed = 0.6
        self.vent_fan_cntrl_seq = "Continuous"
        self.clg_fan_min_speed = 0.6
        self.clg_fan_max_speed = 1
        self.clg_fan_cntrl_seq = "CFD"
        self.htg_fan_min_speed = .6
        self.htg_fan_max_speed = 1
        self.htg_fan_cntrl_seq = "CFD"
        self.cmp_lockout_temp = 50


    def calculate(self, rtu):
        if (not isinstance(rtu, Rtu.Rtu)):
            raise TypeError("Cannot run TddRtuModel on non-RTU asset")



