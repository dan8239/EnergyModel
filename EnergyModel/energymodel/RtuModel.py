from energymodel import EnergyModel

class RtuModel(EnergyModel):
    """description of class"""
    def __init__(self):
        super().__init__()
        self.kwh_refrig = 0
        self.kwh_fan = 0
        self.kwh_heat = 0
        self.therms_heat = 0