from ecm import Ecm
from assets import Rtu
from utility import Assumptions

class RetroCommission(Ecm.Ecm):
    def __init__(self, eer_gain = Assumptions.FilterAssets.retrofit_efficiency_gain):
        if (eer_gain > 1):
            raise TypeError("retrofit efficiency gain cannot be greater than 1.00 (100%)")
        self.eer_gain = eer_gain
        
    """description of class"""
    def __upgrade_eer(self, asset):
        asset.degr_eer = min(asset.fact_eer, asset.degr_eer * (1 + self.eer_gain))

    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            self.__upgrade_eer(asset)
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")