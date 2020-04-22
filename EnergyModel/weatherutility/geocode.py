import geopy
import config

class Geocode:
    @staticmethod
    def geocode(address):
        #Returns geopy.location.Location object
        #subfields address, altitude, latitude, longitude, point, raw
        
        geocoder = geopy.geocoders.GoogleV3(config.google_api_key)
        loc_obj = geocoder.geocode(query = address, timeout = 10)
        return loc_obj
