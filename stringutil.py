'''
Created on 5 Nov 2017

@author: Simon Meaden
'''

import string
import re

class StringUtil(object):
    '''
    classdocs
    '''


#     def __init__(self, params):
#         '''
#         Constructor
#         '''

    @staticmethod
    def chomp(s):
        if len(s):
            lines = s.splitlines(True)
            last = lines.pop()
            return ''.join(lines + last.splitlines())
        else:
            return ''

    '''
    final_text = split_without("Hey, you - what are you doing?!", string.punctuation)
    # returns ['Hey', 'you', 'what', 'are', 'you', 'doing']
    '''
    @staticmethod
    def split_without(text: str, ignore: str) -> list:

        # Split by whitespace
        split_string = text.split()

        # Strip any characters in the ignore string, and ignore empty strings
        words = []
        for word in split_string:
            word = word.strip(ignore)
            if word != '':
                words.append(word)

        return words

    '''
    text = left(str, 3) will return the leftmost three characters.
    Remember 0 based indexing.
    ignored.
    '''
    @staticmethod
    def left(s, amount):
        return s[:amount]

    '''
    text = right(str, 3) will return the rightmost three characters.
    Remember 0 based indexing. Requesting more characters than there
    are in the string will return the entire string.
    '''
    @staticmethod
    def right(s, amount):
        return s[-amount:]

    '''
    text = mid(str, 2, 3) will return the leftmost three characters.
    Remember 0 based indexing. Requesting data after the end will
    only return values withing the string, extra characters are
    '''
    @staticmethod
    def mid(s, offset, amount):
        return s[offset:offset + amount]

    @staticmethod
    def titlecase(s):
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                   lambda mo: mo.group(0)[0].upper() +
                              mo.group(0)[1:].lower(),
                   s)

if __name__ == '__main__':

    strg = 'This is my test string'
    print('String = ' + strg)
    print('Length : ' + str(len(strg)))
    print('First 4 chars = ' + StringUtil.left(strg, 4))
    print('First 30 chars = ' + StringUtil.left(strg, 30))
    print('Last 6 chars  = ' + StringUtil.right(strg, 6))
    print('Last 30 chars  = ' + StringUtil.right(strg, 30))
    print('Middle 7 chars = ' + StringUtil.mid(strg, 8, 7))
    print('Slice beyond end = ' + StringUtil.mid(strg, 20, 7))


