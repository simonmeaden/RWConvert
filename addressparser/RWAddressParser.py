'''
Created on 28 Dec 2017

@author: Simon Meaden
'''

from address import AddressParser, Address

class RWAddressParser(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass

    def parse(self, street):

#             streetsplit = RWConvertUtils.removeAbbreviations(streetsplit)
#             number = '0 '
#             namedHouse = False
#             if len(streetsplit) > 0:
#                 if streetsplit[0].isnumeric():
#                     number = streetsplit[0] + ' '
#                 else:
#                     namedHouse = True

#         address_details = self.getAddress(postcode)
#         pc_streetdata = address_details.split(',')#StringUtil.split_without(address_details, ',')

    def removeAbbreviations(values = {}):
        l = [RWConvertUtils.removeAbbreviation(item) for item in values]
        return l;

    @staticmethod
    def removeAbbreviation(value):
        '''
        Removes particular abbreviations that I have found.
        This is probably not an exhaustive list as people are
        involved and they enter some strange shit sometimes.
        '''
        v = value.lower()
        if v == 'rd':
            value = 'Road'
        elif v == 'av' or v == 'ave':
            return 'Avenue'
        elif v == 'dr' or v == 'drv':
            return 'Drive'
        elif v == 'wy':
            return 'Way'
        elif v == 'wlk':
            return 'Walk'
        elif v == 'prk':
            return 'Park'
        else:
            return value.capitalize()

    def getAddressFromGoogle(self, query):
        search_payload = {'key':'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', 'query':query}
        search_req = requests.get(self.search_url, params=search_payload)
        search_json = search_req.json()

        form_add = search_json['results'][0]['formatted_address']
        place_id = search_json['results'][0]['place_id']
        self.lat = search_json['results'][0]['geometry']['location']['lat']
        self.lon = search_json['results'][0]['geometry']['location']['lng']

        details_payload = {"key":'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', "placeid":place_id}
        details_resp = requests.get(self.details_url, params=details_payload)
        details_json = details_resp.json()

        self.region = details_json['result']['address_components'][3]['long_name']

        return form_add

    def getCountyFromGoogle(self, town):
        search_payload = {'key':'AIzaSyCAZVZOLgF4htpnLsAGkCZi7ygAsI7aFts', 'address':town}
        search_req = requests.get(self.search_url, params=search_payload)
        search_json = search_req.json()

        #         county = search_json[''][0]['formatted_address']
        county = ''

    #     details_payload = {'key':key, 'placeid':place_id}
    #     details_resp = requests.get(details_url, params=details_payload)
    #     details_json = details_resp.json()

    #     url = details_json['result']['url']
        return county