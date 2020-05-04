from assets import Rtu

class Split(Rtu.Rtu):
    def __init__(self, site = None, auid = 0, tons = 0, eer = 0, econ = False, cmp_stg = False):
        super().__init__()
        self.econ = False


