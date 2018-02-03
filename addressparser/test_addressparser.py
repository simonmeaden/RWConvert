'''
Created on 30 Jan 2018

@author: simon
'''
import pytest
from addressparser.RWAddressParser import RWAddressParser


def test_nospace6():
    postcode = 'TQ45NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == True
    assert postcode == 'TQ4 5NG'
    
def test_withspace6():
    postcode = 'TQ4 5NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == True
    assert postcode == 'TQ4 5NG'
    
def test_nospace7():
    postcode = 'TQ145NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == True
    assert postcode == 'TQ14 5NG'
    
def test_withspace7():
    postcode = 'TQ14 5NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == True
    assert postcode == 'TQ14 5NG'
    
def test_nospaceLetter7():
    postcode = 'TQ1W5NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == True
    assert postcode == 'TQ1W 5NG'
    
def test_withspaceLetter7():
    postcode = 'TQ1W 5NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == True
    assert postcode == 'TQ1W 5NG'
    
def test_short():
    postcode = 'TQ1NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'TQ1NG'
    
def test_long():
    postcode = 'TQ1455NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'TQ1455NG'
    
# test for numbers/letters swapped
def test_misformed(): 
    postcode = '1Q145NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == '1Q145NG'
    postcode = 'T1145NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'T1145NG'
    postcode = 'TQW45NG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'TQW45NG'
    postcode = 'TQ14XNG'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'TQ14XNG'
    postcode = 'TQ1455G'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'TQ1455G'
    postcode = 'TQ145N5'
    result, postcode = RWAddressParser.validatePostcode(postcode)
    assert result == False
    assert postcode == 'TQ145N5'
     
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    pytest.main()