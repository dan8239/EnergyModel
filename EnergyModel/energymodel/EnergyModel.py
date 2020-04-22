class EnergyModel():
    """Generic Energy Model Base Class"""

    def __init__(self):
        self.kwh_annual = 0
        self.therms_annual = 0

    def calculate(self, asset):
        pass
