'''
Created on 10 Dec 2017

@author: simon
'''

# import os
# import sys
# import cdecimal
# sys.modules["decimal"] = cdecimal

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Numeric

engine = create_engine('mysql://simon:REv5=Zeg8@host/rwconvert')
Base = declarative_base()
Session = sessionmaker(bind=some_engine)

class Address(Base):
    __tablename__ = 'Address'

    def __init__(self, postcode, street, city, region, country):
        """
        """
        self.postcode = postcode
        self.street = street
        self.city = city
        self.region = region
        self.country = country

    Id = Column(Integer, primary_key=True)
    postcode = Column(String)
    street = Column(String)
    city = Column(String)
    region = Column(String)
    country = Column(String)

class Housename(Base):
    __tablename__ = 'Housename'

    def __init__(self, street_id, housename, latutude, longitude):
        """
        """
        self.street_id = street_id
        self.housename = housename
        self.longitude = longitude
        self.latutude = latutude

    Id = Column(Integer, primary_key = True)
    street_id = Column(Integer)
    housename = Column(String)
    longitude = Column(Numeric(8, 5))
    latutude = Column(Numeric(8, 5))
);


class Database(object):
    '''
    classdocs
    '''
    config = {}
    Base.metadata.bind = engine
    Base.metadata.create_all()

    def __init__(self, config = {}):
        '''
        Constructor
        '''
        self.config = config

    def addAddress(self, postcode, streetname, city, region, country):
        session = Session()

        try:
            address = Address(postcode, streetname, city, region, country)
            session.add(address)

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def addHousename(self, street_id, housename, latitude, longitude):
        session = Session()

        try:
            housename = Housename(street_id, housename, latitude, longitude)
            session.add(housename)

            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    def getStreetId(self, postcode):
        session = Session()

        try:
            address = session.query(Address).filter(Address.postcode == postcode)
            return address.street_id

        except:
            session.rollback()
            raise
        finally:
            session.close()

    def getLocation(self, street_id):
        session = Session()

        try:
            housename = session.query(Housename).filter(Housename.street-id == street_id)
            return (housename.latitude, housename,longitude)

        except:
            session.rollback()
            raise
        finally:
            session.close()


