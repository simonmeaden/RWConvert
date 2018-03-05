'''
Created on 24 Dec 2017

@author: Simon Meaden
'''

import sqlite3
import os
import os.path
import json

# constant values
PATHS = 'Paths'
FILES = 'Files'
FORMS = 'Forms'
NAMES = 'Names'


class Database(object):
    '''
    classdocs
    '''

 
#     get_housenames_from_streetname = open('../scripts/get_housenames_from_streetname.sql', 'r').read()
#     get_housenames_from_postcode = open('../scripts/get_housenames_from_postcode.sql', 'r').read()
#
#     get_streetnames_from_housename = open('../scripts/get_streetnames_from_housename.sql', 'r').read()
#     get_streetnames_from_postcode = open('../scripts/get_streetnames_from_postcode.sql', 'r').read()
#     get_streetname_housename_from_postcode = open('../scripts/get_streetname_housename_from_postcode.sql', 'r').read()

#    self.countries = {}

    def __init__(self, db_path, db_name):
        '''
        Constructor
        '''
        self.create_tables = '''
            CREATE TABLE IF NOT EXISTS "pref_country" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" VARCHAR(50),
                "preferred" VARCHAR(50),
                UNIQUE(name, preferred));
            CREATE TABLE IF NOT EXISTS "housename" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "street_id" INTEGER,
                "name" VARCHAR(50),
                "latitude" INTEGER,
                "longitude" INTEGER,
                UNIQUE (street_id, name)
            );
            CREATE TABLE IF NOT EXISTS "postcode" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "code" VARCHAR(20),
                "def_longitude" INTEGER,
                "def_latitude" INTEGER,
                UNIQUE(code)
            );
            CREATE TABLE IF NOT EXISTS "region" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" VARCHAR(50),
                "country_id" INTEGER,
                UNIQUE(name, country_id));
            CREATE TABLE IF NOT EXISTS "pref_region" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" VARCHAR(50),
                "preferred" VARCHAR(50),
                "country_id" INTEGER,
                UNIQUE(name, preferred, country_id));
            CREATE TABLE IF NOT EXISTS "city" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" VARCHAR(20),
                "region_id" INTEGER,
                UNIQUE(name, region_id)
            );
            CREATE TABLE IF NOT EXISTS "street" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "city_id" INTEGER,
                "postcode_id" INTEGER,
                "name" VARCHAR(50),
                UNIQUE(name, postcode_id)
            );
        '''
        self.create_countries = '''
            CREATE TABLE IF NOT EXISTS countries (
                "common" TEXT,
                "official" TEXT,
                "native_id" INTEGER,
                "tld_id" INTEGER,
                "cca2" CHAR(2),
                "cca3" CHAR(3),
                "ccn3" CHAR(3),
                "cioc" CHAR(3),
                "currency_id" INTEGER,
                "calling_code_id" INTEGER,
                "capital" TEXT,
                "altspellings" INTEGER,
                "region" TEXT,
                "subregion" TEXT,
                "language_id" INTEGER,
                "translations" INTEGER,
                "lat" TEXT,
                "lon" TEXT,
                "demonym" TEXT,
                "landlocked" BOOLEAN,
                "borders" INTEGER,
                "area" INTEGER
            );
            CREATE TABLE IF NOT EXISTS tld (
                "id" INTEGER,
                "tld" CHAR(3)
            );
            CREATE TABLE IF NOT EXISTS native (
                "id" INTEGER,
                "language" CHAR(3),
                "official" TEXT,
                "common" TEXT
            );
            CREATE TABLE IF NOT EXISTS currency (
                "id" INTEGER,
                "name" CHAR(3)
            );
            CREATE TABLE IF NOT EXISTS callingcode (
                "id" INTEGER,
                "code" CHAR(3)
            );
            CREATE TABLE IF NOT EXISTS altspellings (
                "id" INTEGER,
                "altspelling" TEXT
            );
            CREATE TABLE IF NOT EXISTS languages (
                "id" INTEGER,
                "code" CHAR(3),
                "name" TEXT
            );
            CREATE TABLE IF NOT EXISTS translations (
                "id" INTEGER,
                "language" CHAR(3),
                "official" TEXT,
                "common" TEXT
            );
            CREATE TABLE IF NOT EXISTS borders (
                "id" INTEGER,
                "border" CHAR(3)
            );
        '''
        self.getDefLatLon            = ''' SELECT def_latitude, def_longitude FROM postcode WHERE code = ? '''
        self.getPreferredCountry     = ''' SELECT preferred FROM pref_country WHERE name = ? '''
        self.getCountryData          = ''' SELECT common, native_id FROM countries;'''
        self.getCountryId            = ''' SELECT native_id FROM countries WHERE common = ? '''
        self.getRegionId             = ''' SELECT id FROM region WHERE name = ? AND country_id = ? '''
        self.getPreferredRegionId    = ''' SELECT id FROM pref_region WHERE name = ? AND country_id = ? '''
        self.getPreferredRegionName  = ''' SELECT preferred FROM pref_region WHERE name = ? AND country_id = ? '''
        self.getCityId               = ''' SELECT id FROM city WHERE name = ? AND region_id = ? '''
        self.getPostcodeId           = ''' SELECT id FROM postcode WHERE code = ? '''
        self.getStreetIdFromPostcode = ''' SELECT id, name FROM street WHERE postcode_id = ? '''
        self.getStreetId = ''' SELECT id FROM street WHERE postcode_id = ? AND name = ?'''
    
        self.insertRegionData = '''INSERT OR IGNORE INTO region (name, country_id) VALUES (?, ?) '''
        self.insertPreferredRegion = ''' INSERT INTO pref_region (name, preferred, country_id) VALUES (?, ?, ?)   '''
        self.insertPreferredCountry = ''' INSERT INTO pref_country (name, preferred) VALUES (?, ?)   '''
        self.insertCityData   = '''INSERT OR IGNORE INTO city (name, region_id) VALUES (?, ?)'''
        self.insertDefLatLon = '''INSERT INTO postcode (def_latitude, def_longitude) VALUES ({latitude}, {longitude}) WHERE code = {postcode};'''
        self.insertPostcode = '''INSERT INTO postcode (code, def_latitude, def_longitude) VALUES (?, ?, ?) '''
        self.insertStreetData = ''' INSERT INTO street (name, city_id, postcode_id) VALUES (?, ?, ?) '''
    
        self.conn  = None
        self.cursor = None
 
        self.sqlite_file = os.path.join(db_path, db_name)
        self.countries_file = os.path.join(db_path, 'countries.json')
        self.conn = sqlite3.connect(self.sqlite_file) #, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()
#         sqlite3.register_adapter(bool, int)
#         sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
        self.createDatabase()
        self.countries = self.getCountriesFromDB()

    def createDatabase(self):
        '''
        '''
        try:
            self.cursor.executescript(self.create_tables)
            self.cursor.executescript(self.create_countries)

            self.cursor.execute('''SELECT max(native_id) FROM countries;''')
            native_id = self.cursor.fetchone()[0]
            if native_id == None: # only reload country data if it is not already done
                self.importCountries()

        except Exception as e:
            errorMessage = str(e)
#             msgbox = QMessageBox.warning(None, 'SQL Warning', errorMessage, QMessageBox.Ok)
            raise

        finally:
            self.conn.commit()

    def getCountriesFromDB(self):

        try:
            qry = self.getCountryData
            self.cursor.execute(qry)
            rows = self.cursor.fetchall()
            return rows

        except Exception as e:
#             MessageBoxW = ctypes.windll.user32.MessageBoxW
#             errorMessage = databaseFile + ': ' + str(e)
#             MessageBoxW(None, errorMessage, 'Error', 0)
#             msgbox = QMessageBox.warning(None, 'SQL Warning', errorMessage, QMessageBox.Ok)

            raise

    def getDefaultLatLonFromDB(self, pcode):

        try:
            qry = self.getDefLatLon
            self.cursor.execute(qry, (pcode,))
            latlon = self.cursor.fetchall()
            if latlon:
               return latlon[0]
            else:
               return None

        except Exception as e:
#             MessageBoxW = ctypes.windll.user32.MessageBoxW
#             errorMessage = databaseFile + ': ' + str(e)
#             MessageBoxW(None, errorMessage, 'Error', 0)
#             msgbox = QMessageBox.warning(None, 'SQL Warning', errorMessage, QMessageBox.Ok)

            raise

    def getCountryIdFromDB(self, name):
        try:
            qry = self.getCountryId
            self.cursor.execute(qry, (name,))
            data = self.cursor.fetchone()
            if data:
                country_id = data[0]
                return country_id
            else:
                return None
        except Exception as e:
            pass

    def insertRegionIntoDB(self, name, country_id):
        try:
            qry = self.insertRegionData
            self.cursor.execute(qry, (name, country_id))
            self.conn.commit()
            qry = self.getRegionId
            self.cursor.execute(qry, (name, country_id))
            id = self.cursor.fetchone()
            if id:
                return id[0]
            else:
                return None
        except Exception as e:
            pass

    def insertPreferredRegionIntoDB(self, name, preferred, country_id):
        try:
            qry = self.insertPreferredRegion
            self.cursor.execute(qry, (name, preferred, country_id,))
            self.conn.commit()
            qry = self.getPreferredRegionId
            self.cursor.execute(qry, (name, country_id))
            id = self.cursor.fetchone()
            if id:
                return id[0]
            else:
                return None
        except Exception as e:
            pass

    def getRegionIdFromDB(self, name, country_id):
        try:
            qry = self.getRegionId
            self.cursor.execute(qry, (name, country_id,))
            id = self.cursor.fetchone()
            if id:
                return id[0]
            else:
                return None
        except Exception as e:
            pass

    def getPreferredRegionFromDB(self, name, country_id):
        try:
            qry = self.getPreferredRegionName
            self.cursor.execute(qry, (name, country_id))
            preferred = self.cursor.fetchone()
            if preferred:
                return preferred[0]
            else:
                return None
        except Exception as e:
            pass

    def insertPreferredCountryIntoDB(self, name, preferred):
        try:
            qry = self.insertPreferredCountry
            self.cursor.execute(qry, (name, preferred))
            self.conn.commit()
            qry = self.getPreferredCountryId
            self.cursor.execute(qry, (name,))
            id = self.cursor.fetchone()
            if id:
                return id[0]
            else:
                return None
        except Exception as e:
            pass

    def getPreferredCountryFromDB(self, name):
        try:
            qry = self.getPreferredCountry
            self.cursor.execute(qry, (name,))
            preferred = self.cursor.fetchone()
            if preferred:
                return preferred[0]
            else:
                return None
        except Exception as e:
            pass

    def insertCityIntoDB(self, name, region_id):
        try:
            qry = self.insertCityData
            self.cursor.execute(qry, (name, region_id))
            self.conn.commit()
            return self.getCityIdFromDB(name, region_id)
        except Exception as e:
            pass

    def getCityIdFromDB(self, name, region_id):
        try:
            qry = self.getCityId
            self.cursor.execute(qry, (name, region_id))
            id = self.cursor.fetchone()
            if id:
                return id[0]
            else:
                return None
        except Exception as e:
            pass

    def insertStreetIntoDB(self, streetname, city_id, postcode, def_lat, def_lon):
        try:
            qry = self.getPostcodeId
            self.cursor.execute(qry, (postcode,))
            pc_data = self.cursor.fetchone()
            street_exists = False
            street_id = -1
            postcode_id = -1
            if pc_data: # postcode already exists
                postcode_id = pc_data[0]
                qry = self.getStreetIdFromPostcode
                self.cursor.execute(qry, (postcode_id,))
                street_data = self.cursor.fetchall()
                if street_data: # some street data exists for this postcode
                    for st_id, name in street_data:
                        if name == streetname:
                            street_exists = True
                            street_name = name
                            street_id = st_id
                            break
            else: # postcode does not exist
                qry = self.insertPostcode
                self.cursor.execute(qry, (postcode, def_lat, def_lon,))
                self.conn.commit()
                qry = self.getPostcodeId
                self.cursor.execute(qry, (postcode,))
                pc_data = self.cursor.fetchone()
                if pc_data:
                    postcode_id = pc_data[0]

            if not street_exists: # the postcode exists but npot this particular street
                qry = self.insertStreetData # so insert new street data
                self.cursor.execute(qry, (streetname, city_id, postcode_id,))
                self.conn.commit()
                qry = self.getStreetId # get it's new id ??
                self.cursor.execute(qry, (postcode_id, streetname,))
                street_id = self.cursor.fetchone()
                if street_id:
                    return street_id[0]
                else:
                    return None

        except Exception as e:
            pass


    def importCountries(self):
        countries_file = open(self.countries_file,'r')
        countries_data = json.load(countries_file)

        for country_data in countries_data:
            name = country_data['name'];
            name_common = name['common']
            name_official = name['official']

            self.cursor.execute('''SELECT max(native_id) FROM countries;''')
            native_id = self.cursor.fetchone()[0]
            if native_id:
                native_id += 1 # iterate to the next value
            else:
                native_id = 1
            native = name['native']
            for code in native:
                native_official = native[code]["official"]
                native_common = native[code]['common']
                self.cursor.execute('''INSERT INTO native (id, language, official, common) VALUES (?, ?, ?, ?)''',
                                (native_id, code, native_official, native_common))

            self.cursor.execute('''SELECT max(tld_id) FROM countries;''')
            tld_id = self.cursor.fetchone()[0]
            if tld_id:
                tld_id += 1 # iterate to the next value
            else:
                tld_id = 1
            tld = country_data['tld']
            for code in tld:
                self.cursor.execute('''INSERT INTO tld (id, tld) VALUES (?, ?)''', (tld_id, code))

            cca2 = country_data['cca2']
            cca3 = country_data['cca3']
            ccn3 = country_data['ccn3']
            cioc = country_data['cioc']

            self.cursor.execute('''SELECT max(currency_id) FROM countries;''')
            currency_id = self.cursor.fetchone()[0]
            if currency_id:
                currency_id += 1 # iterate to the next value
            else:
                currency_id = 1
            currency = country_data['currency']
            for name in currency:
                self.cursor.execute('''INSERT INTO currency (id, name) VALUES (?, ?)''', (currency_id, name))

            self.cursor.execute('''SELECT max(calling_code_id) FROM countries;''')
            calling_code_id = self.cursor.fetchone()[0]
            if calling_code_id:
                calling_code_id += 1 # iterate to the next value
            else:
                calling_code_id = 1
            callingcode = country_data['currency']
            for code in callingcode:
                self.cursor.execute('''INSERT INTO callingcode (id, code) VALUES (?, ?)''', (calling_code_id, code))

            capital = country_data['capital']

            self.cursor.execute('''SELECT max(altspellings) FROM countries;''')
            altspellings_id = self.cursor.fetchone()[0]
            if altspellings_id:
                altspellings_id += 1 # iterate to the next value
            else:
                altspellings_id = 1
            altspellings = country_data['altSpellings']
            for code in altspellings:
                self.cursor.execute('''INSERT INTO altspellings (id, altspelling) VALUES (?, ?)''', (altspellings_id, code))

            region = country_data['region']
            subregion = country_data['subregion']

            self.cursor.execute('''SELECT max(language_id) FROM countries;''')
            language_id = self.cursor.fetchone()[0]
            if language_id:
                language_id += 1 # iterate to the next value
            else:
                language_id = 1
            languages = country_data['languages']
            for lang in languages:
                self.cursor.execute('''INSERT INTO languages (id, code, name) VALUES (?, ?, ?)''', (language_id, lang, languages[lang][0]))

            self.cursor.execute('''SELECT max(translations) FROM countries;''')
            trans_id = self.cursor.fetchone()[0]
            if trans_id:
                trans_id += 1 # iterate to the next value
            else:
                trans_id = 1
            translations = country_data['translations']
            for code in translations:
                tran_official = translations[code]["official"]
                tran_common = translations[code]['common']
                self.cursor.execute('''INSERT INTO native (id, language, official, common) VALUES (?, ?, ?, ?)''',
                                (trans_id, code, tran_official, tran_common))

            lat = country_data['latlng'][0]
            lng = country_data['latlng'][1]
            demonym = country_data['demonym']
            landlocked = country_data['landlocked']

            self.cursor.execute('''SELECT max(borders) FROM countries;''')
            borders_id = self.cursor.fetchone()[0]
            if borders_id:
                borders_id += 1 # iterate to the next value
            else:
                borders_id = 1
            borders_id += 1 # iterate to the next value
            borders = country_data['borders']
            for code in borders:
                self.cursor.execute('''INSERT INTO borders (id, border) VALUES (?, ?)''', (borders_id, code))

            area = country_data['area']

            self.cursor.execute('''INSERT INTO countries (
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


    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':

    from addressparser.RWAddressParser import RWAddressParser
    from stringutil import StringUtil
    from postal.expand import expand_address
    from postal.parser import parse_address

    db_path = '/home/simon/.config/RWConvert/data'
    db_name = 'rwconvert.sqlite'
    db = Database(db_path, db_name)
    parser = RWAddressParser(db_path, db_name)
    
    db.insertPreferredCountryIntoDB('England', 'United Kingdom')
    db.insertPreferredCountryIntoDB('Scotland', 'United Kingdom')
    db.insertPreferredCountryIntoDB('Wales', 'United Kingdom')
   
    postcode = 'TQ45NG'
    postcodevalid, postcode = RWAddressParser.validatePostcode(postcode)
    g_address = parser.getGoogleAddressFromPostcode(postcode)
    country = g_address.country
    preferred = db.getPreferredCountryFromDB(country)
    if preferred:
        country = preferred
    country_id = db.getCountryIdFromDB(country)


    region_id = db.insertRegionIntoDB('Devon', country_id)
    region_id = db.insertPreferredRegionIntoDB('Torbay', 'Devon', country_id)

    region = 'Torbay'
    preferred = db.getPreferredRegionFromDB(region, country_id)
    if preferred != None:
        region = preferred
    region_id = db.getRegionIdFromDB(region, country_id)

    city_id = db.insertCityIntoDB('Torquay', region_id)
    city_id = db.insertCityIntoDB('Paignton', region_id)
    city_id = db.insertCityIntoDB('Brixham', region_id)
    city_id = db.insertCityIntoDB('Kingswear', region_id)
    city_id = db.insertCityIntoDB('Dartmouth', region_id)

    city_id = db.insertCityIntoDB('Dartmouth', region_id) # should be ignored as is a repeat

    region = g_address.region2
    preferred = db.getPreferredRegionFromDB(region, country_id)
    if preferred != None:
        region = preferred
    region_id = db.getRegionIdFromDB(region, country_id)
    city = g_address.city
    city_id = db.getCityIdFromDB(city, region_id)
    street = g_address.street
    s_address = expand_address(street)[0] # pypostal expands rd to road etc
    s_address = StringUtil.titlecase(s_address)
    def_lat = g_address.lat
    def_lon = g_address.lon

    street_id = db.insertStreetIntoDB(s_address, city_id, postcode, def_lat, def_lon)

    lat,lon = db.getDefaultLatLonFromDB(postcode)
    print(lat)
    print(lon)

    db.close()




