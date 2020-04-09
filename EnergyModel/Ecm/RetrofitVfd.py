from ecm import ecm
from assets import Asset
import utilityfunctions

class RetrofitVfd(ecm.Ecm):
    """description of class"""
    def __upgrade_eer(self, asset):
        eer_gain = asset.proposal.site.assumptions.self.retrofit_efficiency_gain
        asset.eer = min()

    def apply_ecm(self, asset):
        if (isinstance(asset, Rtu)):
            asset.vfd = True
        else:
            raise NotImplementedError("ECM Type not supported for Asset Type")
