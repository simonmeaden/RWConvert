'''
Created on 5 Nov 2017

@author: Simon Meaden
'''

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

# '''
# Splits a string into component words removing any punctuation
# split_without_punc("Hey, you -- what are you doing?!")
# '''
# split_without_punc = lambda text : [word.strip(string.punctuation) for word in
#     text.split() if word.strip(string.punctuation) != '']