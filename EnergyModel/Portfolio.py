from Site import *

class Portfolio():
    def __init__(self, id):
        self.id = id
        self.site_list = dllist()

    def add_site(self, site):
        if (not isinstance(site, Site)):
            raise TypeError("Cannot add a non Site type to portfolio Site_list")
        self.site_list.appendright(site)
        site.portfolio = self

    def find_site(self, site_name):
        for x in self.site_list.iternodes():
            if (x.value.id == site_name):
                return x.value
        return None

    def dump(self):
        print("ID: " + str(self.id))
        print("Total Sites:" + str(self.site_list.size))
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.dump()
        print()
