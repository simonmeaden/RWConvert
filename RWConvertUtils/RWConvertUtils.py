'''
Created on 26 Dec 2017

@author: Simon Meaden
'''

import string

class RWConvertUtils(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass

    @staticmethod
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