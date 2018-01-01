'''
Created on 28 Dec 2017

@author: Simon Meaden
'''

# from address import AddressParser, Address
from postal.expand import expand_address
from postal.parser import parse_address
import requests
import collections
import string
from enum import Enum
from db.database import Database
import convert_iplugin

class RWAddressParser(object):
    '''
    Parses the supplied address using various sources and libraries
    pypostal libpostal) is used to parse the address. Google Maps is
    used to get certain data from the postcode. The supplied address is
    also parsed and expanded to supply house names or numbers and
    full street types ('rd' to 'road' etc.).
    '''
    search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?'
    county_search_url = 'https://maps.googleapis.com/maps/api/geocode/json' #?address=Winnetka&key=YOUR_API_KEY
#]
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def parse(self, street, postcode, customer = ''):

        ''' Download data from Google, expand name forms 'Rd' to 'road' etc.
        Parse using pypostal to more manageable forms. '''
        g_address = self.getAddressFromGoogle(postcode)
        ge_address = expand_address(g_address.form_add)
        gp_address = parse_address(ge_address[0])
        ''' Expand supplied address, expand also and parse into more
        manageable forms '''
        s_address = expand_address(street)[0] # pypostal expands rd to road etc
        sp_address = parse_address(s_address)

        # Combine the two data sets.
        address_data = sp_address + gp_address;

        # detect which address form we have, store into g_address
        for name, add_type in address_data:
            if add_type == 'house_number':
                g_address.type = AddressType.HOUSE_NUMBER
                g_address.housenumber = name
            elif add_type == 'house_name':
                g_address.type = AddressType.HOUSE_NAME
                g_address.housename = name
            elif add_type == 'road':
                g_address.street = name
            elif add_type == 'city':
                g_address.city = name
            elif add_type == 'country':
                g_address.country = 'United Kingdom'


        ''' OK a weird user cock-up that occasionally comes up. The user enters their house number
        into the name slot. Just check for a numeric name. May need to expand this later
        depending on occurrences. '''
        if g_address.type == AddressType.NONE:
            if customer.isnumeric():
                g_address.type = AddressType.HOUSE_NUMBER
                g_address.housenumber = customer

        ''' This is the simplest and most common form, house name and street
        name. Just pass this back'''
        if g_address.type == AddressType.HOUSE_NUMBER:
            return g_address

        ''' The next most common is the house name + street name. This will need
        to check the internal database to see if the house name is registered.'''
        if g_address.type == AddressType.HOUSE_NAME:
            db = Database()


    def getAddressFromGoogle(self, postcode):
        address = GAddress()
        search_payload = {'key':'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', 'query':postcode}
        search_req = requests.get(self.search_url, params=search_payload)
        search_json = search_req.json()

        address.form_add = search_json['results'][0]['formatted_address']
        address.place_id = search_json['results'][0]['place_id']
        address.lat = search_json['results'][0]['geometry']['location']['lat']
        address.lon = search_json['results'][0]['geometry']['location']['lng']

        details_payload = {"key":'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', "placeid":address.place_id}
        details_resp = requests.get(self.details_url, params=details_payload)
        details_json = details_resp.json()

        for item in details_json['result']['address_components']:
            if item['types'][0] == 'postal_code':
                continue
            elif item['types'][0] == 'route':
                address.street = item['long_name']
            elif item['types'][0] == 'postal_town':
                address.city = item['long_name']
            elif item['types'][0] == 'country':
                address.country = item['long_name']
            elif item['types'][0] == 'administrative_area_level_1':
                address.region1 = item['long_name']
            elif item['types'][0] == 'administrative_area_level_2':
                address.region2 = item['long_name']

        return address

