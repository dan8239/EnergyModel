from ecm import Ecm
from assets import Rtu

class RetroCommission(Ecm.Ecm):
    def __init__(self):
        pass
        
    """description of class"""
    def __upgrade_eer(self, asset):
        eer_gain = asset.proposal.site.assumptions.retrofit_efficiency_gain
        asset.degr_eer = min(asset.fact_eer, asset.degr_eer * (1 + eer_gain))

    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu.Rtu)):
            self.__upgrade_eer(asset)
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")