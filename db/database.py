'''
Created on 10 Dec 2017

@author: simon
'''

import sqlite3
import os

class Database(object):
    '''
    classdocs
    '''

    config = {}

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def createDatabase(self, config = {}):
        self.config = config
        db = sqlite3.connect(os.path.join(self.config[PATHS]['db_path'],'data/rwconvert'))