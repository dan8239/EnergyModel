from assets import rtu

class Split(rtu.Rtu):
    def __init__(self, site = None, auid = 0, tons = 0, eer = 0, econ = False, vfd = False, stg_cmp = False):
        super().__init__()
        self.econ = False


