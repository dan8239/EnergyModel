from assets import *

class Ecm():
    """Energy Conservation Measure. Apply appropriate changes to new asset based on ECM type"""

    def apply_ecm(self, asset):
        raise NotImplementedError("Concrete Class Method Not Implemented")