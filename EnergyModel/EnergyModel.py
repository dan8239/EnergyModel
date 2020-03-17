from Site import *
from Asset import *
from Proposal import *

def main():
    site1 = Site(1)
    asset1 = Asset()
    asset2 = Asset()
    asset3 = Asset()
    asset4 = Asset()
    asset5 = Asset()

    site1.add_asset(asset1)
    site1.add_asset(asset2)
    site1.add_asset(asset3)
    site1.add_asset(asset4)
    site1.add_asset(asset5)

    site1.print_all()

if __name__ == "__main__":
    main()
