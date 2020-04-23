from assets import Asset, Proposal
from utility import Assumptions
from pyllist import dllist, dllistnode
from weatherutility import geocode
from climdata import ClimateData
from energymodel import TddRtuModel

class Site:
    
    #constructor + instance variables
    def __init__(self, id):
        self.id = id
        self.portfolio = None
        self.address = None
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        self.proposal_list = dllist()
        self.climate_data = ClimateData.ClimateData()
        self.assumptions = Assumptions.Assumptions()
        self.energy_model = TddRtuModel.TddRtuModel()

    def geocode(self):
        if (self.address == None):
            raise TypeError("Address not instantiated. Cannot Geocode")
        else:
            locationobj = geocode.Geocode.geocode(self.address)
            self.latitude = locationobj.latitude
            self.longitude = locationobj.longitude
            self. altitude = locationobj.altitude

    def fill_climate_data(self):
        self.climate_data.get_closest_climate_zone(self.latitude, self.longitude)
        self.climate_data.calculate_climate_data()

    def run_energy_calculations(self, energy_model):
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.run_energy_calculations(energy_model)
        self.update_energy_totals()

    def update_energy_totals(self):
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        for x in self.proposal_list.iternodes():
            if (x !=None):
                self.pre_kwh_hvac_yearly = self.pre_kwh_hvac_yearly + x.value.pre_kwh_yearly
                self.post_kwh_hvac_yearly = self.post_kwh_hvac_yearly + x.value.post_kwh_yearly
                self.sav_kwh_hvac_yearly = self.sav_kwh_hvac_yearly + x.value.sav_kwh_yearly
                self.pre_therms_hvac_yearly = self.pre_therms_hvac_yearly + x.value.pre_therms_yearly
                self.post_therms_hvac_yearly = self.post_therms_hvac_yearly + x.value.post_therms_yearly
                self.sav_therms_hvac_yearly = self.sav_therms_hvac_yearly + x.value.sav_therms_yearly
            
    def dump(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXX SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print()
        print("ID: " + str(self.id))
        print("address: " + str(self.address))
        print("latitude: " + str(self.latitude))
        print("longitude: " + str(self.longitude))
        print("altitude: " + str(self.altitude))
        print("Pre KWH: " + str(self.pre_kwh_hvac_yearly))
        print("Post KWH: " + str(self.post_kwh_hvac_yearly))
        print("Saved KWH: " + str(self.sav_kwh_hvac_yearly))
        if (self.climate_data != None):
            self.climate_data.dump()
        print("Total Assets:" + str(self.proposal_list.size))
        
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.dump()
        
        print()
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX END OF SITE OBJECT XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        
    def add_proposal(self, proposal):
        if (not isinstance(proposal, Proposal.Proposal)):
            raise TypeError("Cannot add a non Proposal type to site proposal_list")
        self.proposal_list.appendright(proposal)
        proposal.site = self