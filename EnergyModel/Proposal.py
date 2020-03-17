class Proposal:
    def __init__(self, strategy = "No Action", new_asset = None, cost = 0):
        self.strategy = strategy
        self.new_asset = new_asset
        self.cost = cost
        
    def replace_asset(self, asset, cost):
        self.strategy = "Replace"
        self.new_asset = asset
        self.cost = cost
        
    def retrofit_asset(self, cost):
        self.strategy = "Retrofit"
        self.new_asset = None
        self.cost = cost
        
    def clear_strategy(self):
        self.strategy = "No Action"
        self.new_asset = None
        self.cost = 0
        
    def printAll(self):
        print("Strategy: " + self.strategy)
        print("New Asset: " + new_asset)
        print("Cost: " + cost)