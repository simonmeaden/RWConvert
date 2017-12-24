'''
Created on 24 Dec 2017

@author: Simon Meaden
'''

import sqlite3
import os

# constant values
PATHS = 'Paths'
FILES = 'Files'
FORMS = 'Forms'
NAMES = 'Names'


class Database(object):
    '''
    classdocs
    '''



    def __init__(self, db_path, db_name):
        '''
        Constructor
        '''
        self.createDatabase(db_path, db_name)

    def createDatabase(self, db_path, db_name):
        '''
        '''
        sqlite_path = os.path.join(db_path, db_name)
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()

        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY, {nf2} {ft2})'.
                  format(tn='streetname',
                         nf1='id', ft1='INTEGER',
                         nf2='name', ft2='VARCHAR(50)')
        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY, {nf2} {ft2})'.
                  format(tn='postcode',
                         nf1='id', ft1='INTEGER',
                         nf2='name', ft2='VARCHAR(20)')
        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY, {nf2} {ft2})'.
                  format(tn='country',
                         nf1='id', ft1='INTEGER',
                         nf2='name', ft2='VARCHAR(20)')
        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY, {nf2} {ft2})'.
                  format(tn='region',
                         nf1='id', ft1='INTEGER',
                         nf2='name', ft2='VARCHAR(50)')
        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY, {nf2} {ft2})'.
                  format(tn='city',
                         nf1='id', ft1='INTEGER',
                         nf2='name', ft2='VARCHAR(20)')
        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY, {nf2} {ft2})'.
                  format(tn='housenames',
                         nf1='street_id', ft1='INTEGER',
                         nf2='name', ft2='VARCHAR(50)',
                         nf3='latitude', ft3='INTEGER',
                         nf4='longitude', ft4='INTEGER')
        c.execute('CREATE TABLE {tn} ({nf1} {ft1} PRIMARY KEY AUTOINCREMENT, {nf2} {ft2}, {nf3} {ft3}, {nf4} {ft4}, {nf5} {ft5}, {nf6} {ft6})'.
                  format(tn='streetnames',
                         nf1='id', ft1='INTEGER',
                         nf2='postcode', ft2='INTEGER',
                         nf3='streetname', ft3='INTEGER',
                         nf4='region', ft4='INTEGER',
                         nf5='city', ft5='INTEGER',
                         nf6='country', ft6='INTEGER'))


        conn.commit()
        conn.close()

