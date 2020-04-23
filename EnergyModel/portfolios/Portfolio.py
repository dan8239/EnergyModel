from sites import Site
from pyllist import dllist, dllistnode

class Portfolio():
    def __init__(self, id):
        self.id = id
        self.site_list = dllist()
        self.energy_model = None
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0

    def add_site(self, site):
        if (not isinstance(site, Site.Site)):
            raise TypeError("Cannot add a non Site type to portfolio Site_list")
        self.site_list.appendright(site)
        site.portfolio = self

    def find_site(self, site_name):
        for x in self.site_list.iternodes():
            if (x.value.id == site_name):
                return x.value
        return None

    def run_energy_calculations(self):
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.run_energy_calculations(self.energy_model)
        self.update_energy_totals()

    def update_energy_totals(self):
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        for x in self.site_list.iternodes():
            if (x !=None):
                self.pre_kwh_hvac_yearly = self.pre_kwh_hvac_yearly + x.value.pre_kwh_hvac_yearly
                self.post_kwh_hvac_yearly = self.post_kwh_hvac_yearly + x.value.post_kwh_hvac_yearly
                self.sav_kwh_hvac_yearly = self.sav_kwh_hvac_yearly + x.value.sav_kwh_hvac_yearly
                self.pre_therms_hvac_yearly = self.pre_therms_hvac_yearly + x.value.pre_therms_hvac_yearly
                self.post_therms_hvac_yearly = self.post_therms_hvac_yearly + x.value.post_therms_hvac_yearly
                self.sav_therms_hvac_yearly = self.sav_therms_hvac_yearly + x.value.sav_therms_hvac_yearly

    def dump(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("ID: " + str(self.id))
        print("Total Sites:" + str(self.site_list.size))
        print("Pre KWH: " + str(self.pre_kwh_hvac_yearly))
        print("Post KWH: " + str(self.post_kwh_hvac_yearly))
        print("Saved KWH: " + str(self.sav_kwh_hvac_yearly))
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.dump()
        print()
