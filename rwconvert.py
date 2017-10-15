import logging
import sys
from PyQt5.QtWidgets import (
    QApplication, 
    QDesktopWidget,
    QMainWindow,
    QTabWidget,
    QFileDialog,
    QGridLayout,
    QFrame, 
    QPushButton, 
    QListWidget,
    QComboBox,
    QLabel,
    QSizePolicy,
    QMessageBox
    )
# from PyQt5.QtCore import (
#     QMap
#     )
# from convert_iplugin import ConvertInterface
from pluginbase import PluginBase
from functools import partial

from openpyxl import Workbook
import os, sys
import configparser
from datetime import date



class ConverterWidget(QMainWindow):
    
    # For easier usage calculate the path relative to here.
    here = os.path.abspath(os.path.dirname(__file__))
    get_path = partial(os.path.join, here)


    # Setup a plugin base for "rwconvert.plugins" and make sure to load
    # all the default built-in plugins from the builtin_plugins folder.
    plugin_base = PluginBase(package='rwconvert.plugins',
                             searchpath=[get_path('./plugins')])

    plugins = {}
    filetypes = []
    filenames = []

    def __init__(self):
        '''
        init
        '''
        
        self.name = 'RWConvert'
        super().__init__()
                                
        self.config = configparser.ConfigParser()
        self.dict = {}
        self.homepath = os.path.expanduser('~') #
        self.docpath = os.path.join(self.homepath, 'Documents')
        self.savepath = os.path.join(self.docpath, 'rwconvert')
        self.downloadpath = os.path.join(self.homepath, 'Downloads')
        self.configpath = os.path.join(self.savepath, 'config.ini')
        self.savefile = 'roadwarrior.xslx'
        self.include_date = True
        self.include_routes = True
        self.currentPluginName = ''
        self.currentPlugin = None
        
        # and a source which loads the plugins from the "plugins"
        # folder.  We also pass the application name as identifier.  This
        # is optional but by doing this out plugins have consistent
        # internal module names which allows pickle to work.
        self.source = self.plugin_base.make_plugin_source(
            searchpath=[self.get_path('./plugins')],
            identifier=self.name)

        # Here we list all the plugins the source knows about, load them
        # and the use the "setup" function provided by the plugin to
        # initialize the plugin.
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            my_class = getattr(plugin, plugin_name)
            instance = my_class()
            self.plugins[plugin_name] = instance
#             plugin.setup(self)

        self.initGui()
#         self.showFullScreen()
        self.import_config()
        


        
    def initGui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Road warrior Upload File Converter')
        self.center()
        
        fMain = QFrame()
        mainLayout = QGridLayout()
        fMain.setLayout(mainLayout)
        self.setCentralWidget(fMain)

        tabWidget = QTabWidget()
        mainLayout.addWidget(tabWidget, 0, 0)
        
        self.closeBtn = QPushButton('Close Application')
        self.closeBtn.clicked.connect(self.handleClose)
        mainLayout.addWidget(self.closeBtn, 1, 0)
        
        fConvert = QFrame()
        convertLayout = QGridLayout()
        fConvert.setLayout(convertLayout)        
        
        fConfig = QFrame()
        configLayout = QGridLayout()
        fConfig.setLayout(configLayout)

        tabWidget.addTab(fConvert, 'Converter')
        tabWidget.addTab(fConfig, 'Configuration')
        
        row = 0
        
        conLbl = QLabel('Converter :')
        convertLayout.addWidget(conLbl, row, 0)
        self.currentPluginBox = QComboBox()
        self.currentPluginBox.currentTextChanged.connect(self.selectPlugin)
        convertLayout.addWidget(self.currentPluginBox, row, 1, 1, 2)
        for key in self.plugins.keys():                    
            self.currentPluginBox.addItem(key)

        row += 1
                                
        self.conFilesLbl = QLabel('Source Files :')
        convertLayout.addWidget(self.conFilesLbl, row, 0)
        self.srcFilesList = QListWidget()
        convertLayout.addWidget(self.srcFilesList, row, 1)
        self.srcFilesBtn = QPushButton('Select Files')
        self.srcFilesBtn.clicked.connect(lambda:self.selectSrcFiles(self.srcFilesBtn))
        self.srcFilesBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        convertLayout.addWidget(self.srcFilesBtn, row, 2)
        row += 1
            
        self.conBtn = QPushButton('Convert')
        convertLayout.addWidget(self.conBtn, row, 0, 1, 3)
        
    def handleClose(self, btn):
        buttonReply = QMessageBox.warning(self, 
                                          'Close Application', 
                                          'You are about to close the Application,'
                                          ' Press Yes to continue or Cancel to return to the Application',
                                           QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Yes:
            self.export_config()
            exit()
        
        
    def selectSrcFiles(self, btn):
        fileDlg = QFileDialog(self, 'Select Files', self.downloadpath, self.filetypes)
        fileDlg.setFileMode(QFileDialog.AnyFile)
        filenames = []

        if fileDlg.exec_():
            filenames = fileDlg.selectedFiles()
            
        self.srcFilesList.addItems(filenames)
        
    def selectPlugin(self, name):
            # deactivate all current active plugins
            if self.currentPluginName in self.plugins.keys():
                self.pluginManager.deactivatePluginByName(self.currentPluginName)
            # activate the current plugin
#             self.pluginManager.activatePluginByName(name)
            self.currentPluginName = name
            self.currentPlugin = self.plugins[name]
            self.filetypes = self.currentPlugin.filetypes
            
    def center(self):    
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def import_config(self):
        if os.path.exists(self.configpath):
#            cfgfile = open(self.configpath,'r')
#            self.config.read(cfgfile)
            self.config.read(self.configpath)
            sections = self.config.sections()
            for section in sections:
                if self.config.has_section(section):
                    if section == 'Paths':
                        self.savefile = self.config['Paths']['savefile']
                        self.downloadpath = self.config['Paths']['download']
                        self.savepath = self.config['Paths']['savepath']
                        self.configfile = self.config['Paths']['configfile']
                    elif section == 'Names':
                        self.include_date = self.config.getboolean('Names', 'include_date')
                        self.include_routes = self.config.getboolean('Names', 'include_routes')
                    elif section == 'Current':
                        name = self.config['Current']['Current Plugin']
                        if name:
                            self.currentPluginName = name
                        # activate the current plugin
#                         self.pluginManager.activatePluginByName(self.currentPluginName)
#                         self.currentPlugin = self.pluginManager.getPluginByName(self.currentPluginName)
                        if self.currentPlugin != None:
                            self.filetypes = self.currentPlugin.filetypes

        else:
            self.config.write(self.configpath)
    
    def export_config(self):
        sections = self.config.sections()
        if not 'Paths' in sections:
            self.config.add_section('Paths')
        if not 'Names' in sections:
            self.config.add_section('Names')
        if not 'Current' in sections:
            self.config.add_section('Current')

        self.config.set('Paths', 'savefile', self.savefile)
        self.config.set('Paths', 'download', self.downloadpath)
        self.config.set('Paths', 'savepath', self.savepath)
        self.config.set('Paths', 'configfile', self.configpath)
        if self.include_date:
            self.config.set('Names', 'include_date',  'yes')
        else:
            self.config.set('Names', 'include_date',  'no')
        if self.include_routes:
            self.config.set('Names', 'include_routes', 'yes')
        else:
            self.config.set('Names', 'include_routes', 'no')
        self.config.set('Current', 'Current Plugin', self.currentPluginName)

        with open(self.configpath, 'w') as configfile:
            self.config.write(configfile)
 
    
    def openFiles(self):
        options = QFileDialog.Options()
        self.filenames = QFileDialog.getOpenFileNames(self, 'Select file', self.downloadpath, self.filetypes, options)
        self.srcFilesList.clear()
        self.srcFilesList.addItems(self.filenames)
        self.currentPlugin.convert(self.filenames)

class ToExcel:
    
    def __init__(self):
        '''
        '''

    def create_workbook(self):
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'Name'
        ws['B1'] = 'Street'
        ws['C1'] = 'City'
        ws['D1'] = 'State/Region'
        ws['E1'] = 'Postal Code'
        ws['F1'] = 'Country Code'
        ws['G1'] = 'Priority (0-1)'
        ws['H1'] = 'Phone'
        ws['I1'] = 'Note'
        ws['J1'] = 'Latitude'
        ws['K1'] = 'Longitude'
        ws['L1'] = 'Service Time'
        col_list = 'ABCDEFGHIJKL'
        for row in range(0,  len(self.data) - 1):
            for col in range(0, 9):
                cell = col_list[col] + str(row + 2)   
                c = self.data[row][col]     
                ws[cell] = c
        
        path = self.savefile
        if self.include_date or self.include_routes:
            path = 'rw'
            if self.include_date:
                d = date.today()
                day = d.day
                month = d.month
                year = d.year
                path += '_'
                if day < 10:
                    path += '0'
                path += str(day)
                if month < 10:
                    path += '0'
                path += str(month)
                path += str(year)
                
            if self.include_routes:
                for route in self.routes:
                    path += '_' + route
                    
            path += '.xlsx'
            
        path = os.path.join(self.savepath, path)
        wb.save(path)


logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    
    w = ConverterWidget()
    w.show()
    
    sys.exit(app.exec_())
