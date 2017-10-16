'''
Created on 5 Oct 2017

@author: Simon Meaden
'''
import abc
from convert_iplugin import ConvertInterface
from chomp import chomp



class HermesUKPlugin(ConvertInterface):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        ''' 
        self.pluginname = 'Hermes (UK) manifest CSV Converter'
        self.plugindescription = ('Converts Hermes (UK) CSV manifest files into '
                                  ' a format that Road Warrior online Upload facility understands,'
                                  ' basically an Excel xlsx file.')
        self.filetypes = 'Manifest CSV Files (manifest*.csv)'
       
    def parse_file(self,  fo):
        lines = fo.readlines()
        data = []
        for line in lines:
            blocks = line.split(",")
            route = blocks[8][3:6]
            sender = blocks[6] # the compay/person sending the package - added to note
            info = blocks[7]
            user_info = blocks[9]
            name = blocks[3]
            street = blocks[4]
            town = 'Paignton'
            region = 'Devon'
            postcode = blocks[5]
            country = 'GB'
            priority = '1.0'
            # Uninitialised hermes deliveries are defined by XXXXXXXXXXXXXXXXXXXX
            # the road warrior importer cannot handle them.
            if name[0] == 'X' and name[1] == 'X' and name[2] == 'X' and name[4] == 'X':
                continue
            notes = route + " : " + sender + " : " + info+ " : " + user_info
            rowlist = []
            rowlist.append(name)     # pluginname
            rowlist.append(street)     # street
            rowlist.append(town) # town/city
            rowlist.append(region)       # County/State
            rowlist.append(blocks[0])     # postcode
            rowlist.append(country)            # Country
            rowlist.append(priority)              # Priority
            rowlist.append(postcode)    # Phone number
            rowlist.append(chomp.chomp(notes))
            data.append(rowlist)
        self.m_rwdata[route] = data
  
    def convert(self, filenames):
        """
        actual conversion is done here
        """
        self.rwdata = {} # empty rwdata
        for filename in filenames:
            fo = open(filename,  "r")
            self.parse_file(fo)
            fo.close()
         
