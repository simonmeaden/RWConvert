'''
Created on 24 Dec 2017

@author: Simon Meaden
'''

import sqlite3
import os
import os.path
from PyQt5.Qt import (
    QMessageBox,
    )

# constant values
PATHS = 'Paths'
FILES = 'Files'
FORMS = 'Forms'
NAMES = 'Names'


class Database(object):
    '''
    classdocs
    '''

    create_tables = open('scripts/create_tables.sql', 'r').read()
    get_housenames_from_streetname = open('scripts/get_housenames_from_streetname.sql', 'r').read()
    get_housenames_from_postcode = open('scripts/get_housenames_from_postcode.sql', 'r').read()

    get_streetnames_from_housename = open('scripts/get_streetnames_from_housename.sql', 'r').read()
    get_streetnames_from_postcode = open('scripts/get_streetnames_from_postcode.sql', 'r').read()
    get_streetname_housename_from_postcode = open('scripts/get_streetname_housename_from_postcode.sql', 'r').read()

    def __init__(self, db_path, db_name):
        '''
        Constructor
        '''
        self.createDatabase(db_path, db_name)

    def createDatabase(self, db_path, db_name):
        '''
        '''
        sqlite_file = os.path.join(db_path, db_name)
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        try:
            cursor.executescript(self.create_tables)

        except Exception as e:
            errorMessage = self.create_tables_file + ': ' + str(e)
            msgbox = QMessageBox.warning(None, 'SQL Warning', errorMessage, QMessageBox.Ok)
            cursor.close()
            raise

        conn.commit()
        conn.close()

