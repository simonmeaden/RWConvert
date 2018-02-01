'''
Created on 30 Jan 2018

@author: Simon Meaden
'''

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication
 
class CommSignals(QObject):
    '''
    classdocs
    '''
    
    errorSignal = pyqtSignal('QString')


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
#     def receiveError(self, QString):
#         emit 