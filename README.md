# RWConvert

This is a Python 3 plugin project to handle the conversion of various
file formats to the Excel 'xlsax files required for Road Warrior
Upload files.

You will need the following requirements.

Python 3
OpenPyxl		sudo pip3 install openpyxl
PyQt5			sudo pip3 install pyqt5
pluginbase		sudo pip3 install pluginbase

So far the only files it handles are Hermes (UK) CSV manifold files but 
the conversion handler is based on a simple plugin architecture which can
be simply updated to to allow other formats to be handled.

Thye rwconvert.py module handles the loading of file or files  and basically 
just calls the convert(filenames) method that is part of the plugin.

All plugins need to subclass ConvertInterface creating a new plugin name,
description and a filter for the file types that you need. The convert(filenames)
method will need to handle the conversion of whatever files you have to
a python dict which maps a route name string to a two dimensional list of 
string values.

Road Warrior upload requires a two dimensional Excel xlsx worksheet with
12 columns. (Name, Street, City, State/Region, Postal Code, Country Code, 
Priority (0-1), Phone, Note, Latitude, Longitude, Service Time) with the last 3
optional.


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
 
 	def convert(self, filenames):
        """
        actual conversion is done here
        """
        self.rwdata = {} # empty rwdata
        for filename in filenames:
            fo = open(filename,  "r")
            self.parse_file(fo)
            fo.close()
         