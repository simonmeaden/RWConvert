'''
Created on 5 Oct 2017

@author: Simon Meaden
'''
import abc
import string
from PyQt5.Qt import (
    QDialog,
    QLabel,
    QLineEdit,
    QFrame,
    QGridLayout
    )
from convert_iplugin import ConvertInterface
from stringutil import StringUtil
import requests
from db.database import Database
# from RWConvertUtils.RWConvertUtils import RWConvertUtils
from addressparser.RWAddressParser import RWAddressParser

# constant values
PATHS = 'Paths'
FILES = 'Files'
FORMS = 'Forms'
NAMES = 'Names'

class StreetDialog(QDialog):

    def __init__(self, street, streetdata, notes, parent=None):
        super(StreetDialog, self).__init__(parent)
        self.setWindowTitle('My Form')
        self.street = street
        self.streetdata = streetdata
        self.notes = notes
        self.replacement = ''
        self.initGui()
        self.lat = 0.0
        self.lon = 0.0

    def initGui(self):
        l = QGridLayout()
        self.setLayout(l)

        self.setWindowTitle('Incorrect street name format')

        l.addWidget(QLabel('Original Street name'), 0, 0)
        l.addWidget(QLabel(self.street), 0, 1)
        l.addWidget(QLabel('Replacement Street name'), 1, 0)

        self.edit = QLineEdit(self.street)
        l.addWidget(self.edit)
        self.edit.textChanged.connect(self.repStreet)

    def repStreet(self, text):
        self.replacement = text


class HermesUKPlugin(ConvertInterface):
    '''
    classdocs
    '''

    search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?'
    county_search_url = 'https://maps.googleapis.com/maps/api/geocode/json' #?address=Winnetka&key=YOUR_API_KEY
    config = {}


    def __init__(self, config):
        '''
        Constructor
        '''
        super().__init__(config)
        self.pluginname = 'Hermes (UK) manifest CSV Converter'
        self.plugindescription = ('Converts Hermes (UK) CSV manifest files into '
                                  ' a format that Road Warrior online Upload facility understands,'
                                  ' basically an Excel xlsx file.')
        self.filetypes = 'Manifest CSV Files (manifest*.csv)'

        db = Database(self.config[PATHS]['db_path'], self.config[FILES]['db_name'])

    def parse_file(self,  fo):
        lines = fo.readlines()
        data = []
        for line in lines:
            blocks = line.split(',')
            route = blocks[8][3:6]
            sender = blocks[6] # the compay/person sending the package - added to note
            info = blocks[7]
            user_info = blocks[9]
            name = blocks[3]
            street = blocks[4].strip()

            streetsplit = StringUtil.split_without(street, string.punctuation)
#             streetsplit = RWConvertUtils.removeAbbreviations(streetsplit)
#             number = '0 '
#             namedHouse = False
#             if len(streetsplit) > 0:
#                 if streetsplit[0].isnumeric():
#                     number = streetsplit[0] + ' '
#                 else:
#                     namedHouse = True

#             town = 'Paignton'
            self.region = 'Devon'
            postcode = blocks[0]
            phone = blocks[5]
            country = 'UK'#'GB'
            priority = '1.0'
            '''
            Uninitialised hermes deliveries are defined by XXXXXXXXXXXXXXXXXXXX
            the road warrior importer cannot handle them so you will need
            to enter them manually..
            '''
            if name[0] == 'X' and name[1] == 'X' and name[2] == 'X' and name[4] == 'X':
                '''
                show that there were some uninitialised entries???
                '''
                continue
            notes = route + ' : ' + sender + ' : ' + info+ ' : ' + user_info
            rowlist = []
            rowlist.append(name)     # pluginname

            address_details = self.getAddress(postcode)
            pc_streetdata = address_details.split(',')#StringUtil.split_without(address_details, ',')
            street = number + pc_streetdata[0]
            town = pc_streetdata[1].split()[0] # second part is the postcode again

#             streetdata = StringUtil.split_without(street, string.punctuation)
#             if len(pc_streetdata) > 0:
#                 if not pc_streetdata[0].isnumeric():
#                     # do something to recover house number
#                     pass

            rowlist.append(street)     # should be number + street
            rowlist.append(town) # town/city
            rowlist.append(self.region)       # County/State
            rowlist.append(postcode)     # postcode
            rowlist.append(country)            # Country
            rowlist.append(priority)              # Priority
            rowlist.append(phone)    # Phone number
            rowlist.append(StringUtil.chomp(notes))
            rowlist.append(self.lat)
            rowlist.append(self.lon)
            data.append(rowlist)
        self.m_rwdata[route] = data

    def handleDuffAddresses(self, street, streetdata, notes):
#         dlg = StreetDialog(street, streetdata, notes)
#         dlg.show()
        pass

    def getAddress(self, query):
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

    def getCounty(self, town):
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


    def convert(self, filenames):
        '''
        actual conversion is done here
        '''
        self.rwdata = {} # empty rwdata
        for filename in filenames:
            fo = open(filename,  'r')
            self.parse_file(fo)
            fo.close()

