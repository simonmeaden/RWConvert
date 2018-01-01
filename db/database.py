'''
Created on 24 Dec 2017

@author: Simon Meaden
'''

import sqlite3
import os
import os.path
import json
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
    create_countries = open('scripts/countries.sql', 'r').read()
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
        conn = sqlite3.connect(sqlite_file, detect_types=sqlite3.PARSE_DECLTYPES)
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
        cursor = conn.cursor()

        try:
            cursor.executescript(self.create_tables)
            cursor.executescript(self.create_countries)

            cursor.execute('''SELECT max(native_id) FROM countries;''')
            native_id = cursor.fetchone()[0]
            if native_id == None: # only reload country data if it is not already done
                self.importCountries(cursor)

        except Exception as e:
            errorMessage = str(e)
            msgbox = QMessageBox.warning(None, 'SQL Warning', errorMessage, QMessageBox.Ok)
            cursor.close()
            raise

        conn.commit()
        conn.close()

    def importCountries(self, cursor):
        path = 'scripts/countries.json'
        countries_file = open(path,'r')
        countries_data = json.load(countries_file)

        for country_data in countries_data:
            name = country_data['name'];
            name_common = name['common']
            name_official = name['official']

            cursor.execute('''SELECT max(native_id) FROM countries;''')
            native_id = cursor.fetchone()[0]
            if native_id:
                native_id += 1 # iterate to the next value
            else:
                native_id = 1
            native = name['native']
            for code in native:
                native_official = native[code]["official"]
                native_common = native[code]['common']
                cursor.execute('''INSERT INTO native (id, language, official, common) VALUES (?, ?, ?, ?)''',
                                (native_id, code, native_official, native_common))

            cursor.execute('''SELECT max(tld_id) FROM countries;''')
            tld_id = cursor.fetchone()[0]
            if tld_id:
                tld_id += 1 # iterate to the next value
            else:
                tld_id = 1
            tld = country_data['tld']
            for code in tld:
                cursor.execute('''INSERT INTO tld (id, tld) VALUES (?, ?)''', (tld_id, code))

            cca2 = country_data['cca2']
            cca3 = country_data['cca3']
            ccn3 = country_data['ccn3']
            cioc = country_data['cioc']

            cursor.execute('''SELECT max(currency_id) FROM countries;''')
            currency_id = cursor.fetchone()[0]
            if currency_id:
                currency_id += 1 # iterate to the next value
            else:
                currency_id = 1
            currency = country_data['currency']
            for name in currency:
                cursor.execute('''INSERT INTO currency (id, name) VALUES (?, ?)''', (currency_id, name))

            cursor.execute('''SELECT max(calling_code_id) FROM countries;''')
            calling_code_id = cursor.fetchone()[0]
            if calling_code_id:
                calling_code_id += 1 # iterate to the next value
            else:
                calling_code_id = 1
            callingcode = country_data['currency']
            for code in callingcode:
                cursor.execute('''INSERT INTO callingcode (id, code) VALUES (?, ?)''', (calling_code_id, code))

            capital = country_data['capital']

            cursor.execute('''SELECT max(altspellings) FROM countries;''')
            altspellings_id = cursor.fetchone()[0]
            if altspellings_id:
                altspellings_id += 1 # iterate to the next value
            else:
                altspellings_id = 1
            altspellings = country_data['altSpellings']
            for code in altspellings:
                cursor.execute('''INSERT INTO altspellings (id, altspelling) VALUES (?, ?)''', (altspellings_id, code))

            region = country_data['region']
            subregion = country_data['subregion']

            cursor.execute('''SELECT max(language_id) FROM countries;''')
            language_id = cursor.fetchone()[0]
            if language_id:
                language_id += 1 # iterate to the next value
            else:
                language_id = 1
            languages = country_data['languages']
            for lang in languages:
                cursor.execute('''INSERT INTO languages (id, code, name) VALUES (?, ?, ?)''', (language_id, lang, languages[lang][0]))

            cursor.execute('''SELECT max(translations) FROM countries;''')
            trans_id = cursor.fetchone()[0]
            if trans_id:
                trans_id += 1 # iterate to the next value
            else:
                trans_id = 1
            translations = country_data['translations']
            for code in translations:
                tran_official = translations[code]["official"]
                tran_common = translations[code]['common']
                cursor.execute('''INSERT INTO native (id, language, official, common) VALUES (?, ?, ?, ?)''',
                                (trans_id, code, tran_official, tran_common))

            lat = country_data['latlng'][0]
            lng = country_data['latlng'][1]
            demonym = country_data['demonym']
            landlocked = country_data['landlocked']

            cursor.execute('''SELECT max(borders) FROM countries;''')
            borders_id = cursor.fetchone()[0]
            if borders_id:
                borders_id += 1 # iterate to the next value
            else:
                borders_id = 1
            borders_id += 1 # iterate to the next value
            borders = country_data['borders']
            for code in borders:
                cursor.execute('''INSERT INTO borders (id, border) VALUES (?, ?)''', (borders_id, code))

            area = country_data['area']

            cursor.execute('''INSERT INTO countries (
                            common,  official,  native_id,  tld_id,
                            cca2, cca3, ccn3, cioc, currency_id,
                            calling_code_id, capital, altspellings,
                            region, subregion, language_id, translations,
                            lat, lon, demonym, landlocked, borders, area
                            ) VALUES
                            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''',
                            (name_common, name_official, native_id,
                             tld_id, cca2, cca3, ccn3, cioc,
                             currency_id, calling_code_id,
                             capital, altspellings_id, region,
                             subregion, language_id, trans_id, lat, lng,
                             demonym, landlocked, borders_id, area))

# 'SELECT last_insert_rowid()'








