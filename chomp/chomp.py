'''
Created on 9 Oct 2017

@author: simon
'''

def chomp(self,  s):
    if len(s):
        lines = s.splitlines(True)
        last = lines.pop()
        return ''.join(lines + last.splitlines())
    else:
        return ''
