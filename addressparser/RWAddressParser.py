# -*- coding: utf-8 -*-
"""
Created on 28 Dec 2017

@author: Simon Meaden
"""

# from address import AddressParser, Address
from postal.expand import expand_address
from postal.parser import parse_address
import requests
from string import whitespace
from db.database import Database
from convert_iplugin import AddressType, GAddress
from stringutil import StringUtil
import re

class RWAddressParser(object):
    
    """
    Parses the supplied address using various sources and libraries
    pypostal libpostal) is used to parse the address. Google Maps is
    used to get certain data from the postcode. The supplied address is
    also parsed and expanded to supply house names or numbers and
    full street types ('rd' to 'road' etc.).
    """
    search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?'
    db = None


#]
    def __init__(self, db_path, db_name):
        '''
        Constructor
        '''
        self.db = Database(db_path, db_name)


    def parse(self, street, postcode, customer = ''):

        '''Initially try to download default lat/lon from db '''
#         def_latlon = self.db.getDefaultLatLonFromDB(postcode)

        ''' Download data from Google, expand name forms 'Rd' to 'road' etc.
        Parse using pypostal to more manageable forms. '''
        g_address = self.getGoogleAddressFromPostcode(postcode)
#         ll_address = self.getGoogleAddressFromLatLon(g_address.lat, g_address.lon)
        ge_address = expand_address(g_address.form_add)
        gp_address = parse_address(ge_address[0])
        ''' Expand supplied address, expand also and parse into more
        manageable forms '''
        s_address = expand_address(street)[0] # pypostal expands rd to road etc
        sp_address = parse_address(s_address)
        s_address = StringUtil.titlecase(s_address)
        country = g_address.country
        country_id = self.db.getCountryIdFromDB(country)
        region = g_address.region2
        region_id = self.db.insertRegionIntoDB(region, country_id)
        city = StringUtil.titlecase(g_address.city)
        city_id = self.db.insertCityIntoDB(city, region_id)
        def_lat = g_address.lat
        def_lon = g_address.lon
        
        self.db.insertStreetIntoDB(s_address, city_id, postcode, def_lat, def_lon)

        # Combine the two data sets.
        address_data = sp_address + gp_address;

        # detect which address form we have, store into g_address
        for name, add_type in address_data:
            if add_type == 'house_number':
                g_address.type = AddressType.HOUSE_NUMBER
                g_address.house_number = name
            elif add_type == 'house_name':
                g_address.type = AddressType.HOUSE_NAME
                g_address.house_name = StringUtil.titlecase(name)
            elif add_type == 'road':
                g_address.street = StringUtil.titlecase(name)
            elif add_type == 'city':
                g_address.city = StringUtil.titlecase(name)
            elif add_type == 'country':
                g_address.country = StringUtil.titlecase(country)

        g_address.postcode = postcode

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
            pass

    @staticmethod
    def validatePostcode(postcode):
        '''
         check for valid characters. should be one of:
         CCDD DCC two letters two digits space digit two characters
         CCD DCC  two letters one digit space digit two letters
         CCDC DCC two letters one digit one letter space one digit two letters
        '''

        ''' first remove any whitespace '''
        code = postcode.translate(dict.fromkeys(map(ord, whitespace)))
        ''' then make it uppercase '''
        code = code.upper()
        ''' then split the inwardcode from the outwardcode '''
        if len(code) < 6 or len(code) > 7:
            return (False, postcode) # invalid postcode, must be 6 or 7 chars after whitespace removal.
        else:
            inward = StringUtil.right(code, 3)
            if len(code) == 6:
                outward = StringUtil.left(code, 3)
            elif len(code) == 7:
                outward = StringUtil.left(code, 4)

            # inward always one digit + two characters
            p = re.compile('\d[A-Z]{2}')
#             print(p.match(inward))
            if not p.match(inward):
                return (False, postcode)

            p = re.compile('[A-Z]{2}(\d|\d\d|\d[A-Z])')
#             print(p.match(outward))
            if not p.match(outward):
                return (False, postcode)

            return (True, outward + ' ' + inward)


    def getGoogleAddressFromPostcode(self, postcode):
        address = GAddress()
        search_payload = {'key':'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', 'query':postcode}
        search_req = requests.get(self.search_url, params=search_payload)
        search_json = search_req.json()

        if len( search_json['results']) > 0:
            address.form_add = search_json['results'][0]['formatted_address']
            address.place_id = search_json['results'][0]['place_id']
            address.lat = search_json['results'][0]['geometry']['location']['lat']
            address.lon = search_json['results'][0]['geometry']['location']['lng']
    
            details_payload = {"key":'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', "placeid":address.place_id}
            details_resp = requests.get(self.details_url, params=details_payload)
            details_json = details_resp.json()
    
            if len(details_json['result']['address_components']) > 0:
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

    def getGoogleAddressFromLatLon(self, latitude, longitude):
#         address = GAddress()
        base = "http://maps.googleapis.com/maps/api/geocode/json?"
        params = "latlng={lat},{lon}&sensor={sen}".format(
            lat = latitude,
            lon = longitude,
            sen = 'true'
            )
        url = "{base}{params}".format(base=base, params=params)
        response = requests.get(url)
        form_addr = response.json['results'][0]['formatted_address']
        return form_addr
        

    
# if __name__ == '__main__':
# pytest.main()
