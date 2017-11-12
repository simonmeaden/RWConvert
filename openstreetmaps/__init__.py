import geopy
from geopy.geocoders import Nominatim

class LatLon:
    latitude = 0
    longitude = 0

class OpenStreetMaps:
    
    def __init__(self):
        self.nom = Nominatim()
        
    def latlonFromPostcode(self, postcode):
        n = self.nom.geocode(postcode)
        l = LatLon()
        l.latitude = n.latitude
        l.longitude = n.longitude
        return l