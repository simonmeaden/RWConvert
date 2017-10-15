
import abc
from pluginbase import PluginBase


class ConvertInterface(abc.ABC, PluginBase):
    
    m_pluginname = 'Base plugin'
    m_plugindescription = 'Basic plugin does nothing'
    m_filetypes = []
    m_rwdata = []

    
    def __init__(self):
        """
        init
        """
        
    @abc.abstractmethod
    def convert(self, filenames):
        """
        actual conversion is done here in your child class
        """
        
    def __pluginname(self):
        return self.m_pluginname
    
    def __set_pluginname(self, newValue):
        self.m_pluginname = newValue
 
    pluginname = property(__pluginname, __set_pluginname)
 
    def __plugindescription(self):
        return self.m_plugindescription
    
    def __set_plugindescription(self, newValue):
        self.m_plugindescription = newValue

    plugindescription = property(__plugindescription, __set_plugindescription)
    
    def __filetypes(self):
        return self.m_filetypes
    
    def __set_filetypes(self, newValue):
        self.m_filetypes = newValue

    filetypes = property(__filetypes, __set_filetypes)

    def __data(self):
        return self.m_rwdata
    
    def __set_data(self, newValue):
        self.m_data = newValue

    data = property(__data, __set_data)
