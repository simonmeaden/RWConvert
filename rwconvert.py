'''
Created on 5 Oct 2017

@author: Simon Meaden
'''
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
    QAbstractItemView,
    QComboBox,
    QCheckBox,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QMessageBox
    )
from PyQt5.QtCore import pyqtSlot
# from PyQt5.QtCore import (
#     QMap
#     )
# from convert_iplugin import ConvertInterface
from pluginbase import PluginBase
from functools import partial

from openpyxl import Workbook
import os, sys
import configparser
from datetime import date, datetime
from PyQt5.Qt import QLineEdit, QCheckBox



class ConverterWidget(QMainWindow):
    
    # For easier usage calculate the path relative to here.
    here = os.path.abspath(os.path.dirname(__file__))
    get_path = partial(os.path.join, here)


    # Setup a plugin base for "rwconvert.plugins" and make sure to load
    # all the default built-in plugins from the builtin_plugins folder.
    plugin_base = PluginBase(package='rwconvert.plugins',
                             searchpath=[get_path('./plugins')])

    plugins = {}
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
        self.savefile = 'roadwarrior'
        self.saveext = '.xlsx'
        self.prefixDate = False
        self.includeDate = True
        self.includeRoutes = False
        self.combineRoutes = False
        self.currentPluginName = ''
        self.currentPlugin = None
        self.filenames = []
        self.destFilename = ''
        
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
        self.importConfig()
        


        
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
        self.closeBtn.clicked.connect(self.handleCloseClick)
        mainLayout.addWidget(self.closeBtn, 1, 0)
         
        tabWidget.addTab(self.initConvertPage(), 'Converter')
        tabWidget.addTab(self.initConfigPage(), 'Configuration')
        
         
    def initConvertPage(self):
        f = QFrame()
        l = QGridLayout()
        f.setLayout(l)

        row = 0
        
        conLbl = QLabel('Converter :')
        l.addWidget(conLbl, row, 0)
        currentPluginBox = QComboBox()
        currentPluginBox.currentTextChanged.connect(self.selectPlugin)
        l.addWidget(currentPluginBox, row, 1, 1, 2)
        for key in self.plugins.keys():                    
            currentPluginBox.addItem(key)
        row += 1
            
        destFilesLbl = QLabel('Destination File :')
        l.addWidget(destFilesLbl, row, 0)
        self.destFilenameEdit = QLineEdit(self.destFilename)
        self.destFilenameEdit.setEnabled(False)
        self.destFilenameEdit.textChanged.connect(self.handleDestFilenameChanged)
        l.addWidget(self.destFilenameEdit, row, 1, 1, 3)
        row += 1
        
        self.combineRoutesBox = QCheckBox('Combine Routes')
        self.combineRoutesBox.clicked.connect(self.handleCombineRoutesClicked)
        self.combineRoutesBox.setEnabled(False)
        l.addWidget(self.combineRoutesBox, row, 0, 1, 3)
        row += 1
        
        addDateInNameBox = QCheckBox('Add date to filename')
        addDateInNameBox.clicked.connect(self.handleAddDateClicked)
        l.addWidget(addDateInNameBox, row, 0, 1, 3)
        self.prefixDateInNameBox = QCheckBox('Add date to filename')
        self.prefixDateInNameBox.setEnabled(False)
        self.prefixDateInNameBox.setToolTip('Only avalable if add date is checked.\nIf not checked add date will be a suffix.')
        self.prefixDateInNameBox.clicked.connect(self.handlePrefixDateClicked)
        l.addWidget(self.prefixDateInNameBox, row, 1, 1, 2)
        row += 1
        
        addRouteInNameBox = QCheckBox('Add route to filename')
        addRouteInNameBox.clicked.connect(self.handleAddRouteClicked)
        l.addWidget(addRouteInNameBox, row, 0)
        row += 1
        
        lbl = QLabel('Destination path :')
        l.addWidget(lbl, row, 0)
        
        self.destPathLbl = QLabel(self.joinSavePath(self.savepath, self.savefile, self.saveext))
        l.addWidget(self.destPathLbl, row, 1, 1, 3)
                                
        row += 1
        
        conFilesLbl = QLabel('Source Files :')
        l.addWidget(conFilesLbl, row, 0)
        self.srcFilesList = QListWidget()
        self.srcFilesList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.srcFilesList.setAlternatingRowColors(True)
        self.srcFilesList.model().rowsInserted.connect(self.handleSrcFilesChanged)
        self.srcFilesList.model().rowsRemoved.connect(self.handleSrcFilesChanged)
        selectionModel = self.srcFilesList.selectionModel()
        selectionModel.selectionChanged.connect(self.handleSrcFilesSelectionChanged)
        l.addWidget(self.srcFilesList, row, 1, 3, 1)
        
        self.srcFilesBtn = QPushButton('Select Files')
        self.srcFilesBtn.clicked.connect(self.selectSrcFiles)
        self.srcFilesBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        l.addWidget(self.srcFilesBtn, row, 2)
        row += 1
            
        self.addFilesBtn = QPushButton('Add Files')
        self.addFilesBtn.clicked.connect(self.addSrcFiles)
        self.addFilesBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        l.addWidget(self.addFilesBtn, row, 2)
        row += 1
            
        self.removeFilesBtn = QPushButton('Remove Files')
        self.removeFilesBtn.setEnabled(False)
        self.removeFilesBtn.clicked.connect(self.removeSrcFiles)
        self.removeFilesBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        l.addWidget(self.removeFilesBtn, row, 2)
        row += 1
            
        self.convertBtn = QPushButton('Convert')
        self.convertBtn.clicked.connect(self.handleConvertClick)
        self.convertBtn.setEnabled(False)
        l.addWidget(self.convertBtn, row, 0, 1, 3)

        return f
    
    def joinSavePath(self, path, filename, ext):
        newpath = os.path.join(path, filename)
        newpath += ext
        return newpath

    def initConfigPage(self):
        f = QFrame()
        l = QGridLayout()
        f.setLayout(l)

        return f
      
    def handleAddDateClicked(self, checked):
        if checked:
            self.includeDate = True
            self.prefixDateInNameBox.setEnabled(True)
        else:
            self.includeDate = False
            self.prefixDateInNameBox.setEnabled(False)
            
    def handlePrefixDateClicked(self, checked):
        if checked:
            self.prefixDate = True
        else:
            self.prefixDate = False
            
    def handleAddRouteClicked(self, checked):
        if checked:
            self.includeRoutes = True
        else:
            self.includeRoutes = False
                        
    def handleCombineRoutesClicked(self, checked):
        if checked:
            self.combineRoutes = True
        else:
            self.combineRoutes = False
            
        self.enableStuff()
            
    def enableStuff(self):     
        if self.srcFilesList.model().rowCount() == 0:
            self.convertBtn.setEnabled(False)
            self.combineRoutesBox.setEnabled(False)
            self.destFilenameEdit.setEnabled(False)
        elif self.srcFilesList.model().rowCount() == 1:
            self.convertBtn.setEnabled(True)
            self.combineRoutesBox.setEnabled(False)
            self.destFilenameEdit.setEnabled(True)
        else:
            self.convertBtn.setEnabled(True)
            self.combineRoutesBox.setEnabled(True)
            if self.combineRoutesBox.isChecked():
                self.destFilenameEdit.setEnabled(True)
            else:
                self.destFilenameEdit.setEnabled(False)
            
    def handleDestFilenameChanged(self, text):        
        if len(text) > 0:
            if self.includeDate:
                year = datetime.year
                month = datetime.month
                day = datetime.day
                datestr = str(year)
                if month < 10: datestr += '0'
                datestr += str(month)
                if day < 10: datestr += '0'
                datestr += str(day)
                if self.prefixDate:
                    name = datestr + '_' + text
                else :
                    name = text + '_' + datestr
            else:
                name = text
                       
            self.savefile = name
            self.destPathLbl.setText(self.joinSavePath(self.savepath, self.savefile, self.saveext))
          
    def createDestinationFilePath(self):
        return self.joinSavePath(self.savepath, self.savefile, self.saveext)
            
    def handleSrcFilesSelectionChanged(self, selected):
        if len(selected.indexes()) > 0:
            self.removeFilesBtn.setEnabled(True)
        else:
            self.removeFilesBtn.setEnabled(False)
              
    def handleSrcFilesChanged(self):
        self.enableStuff()
        
    @pyqtSlot()
    def handleConvertClick(self):
        if len(self.filenames) > 0:
            toexcel = ToExcel()
     
            self.currentPlugin.convert(self.filenames)
            routedata = self.currentPlugin.rwdata
            
            if self.combineRoutes:
                combined = []
                for route in routedata.keys():
                    l = routedata[route]
                    combined += l
                toexcel.create_workbook(combined, self.joinSavePath(self.savepath, self.savefile, self.saveext))
                
            else:
                i = 1
                for route in routedata.keys():
                    l = routedata[route]
                    if self.includeRoutes and len(route) > 0:
                        self.joinSavePath(self.savepath, self.savefile + '_' + route, self.saveext)
                    else:
                        self.joinSavePath(self.savepath, self.savefile + '(' + str(i) + ')', self.saveext)
                        i += 1
                        
                    toexcel.create_workbook(combined, self.savefile)        
        
    @pyqtSlot()
    def handleConverterChange(self):
        pluginName = self.currentPluginBox.currentText()
        if pluginName != self.currentPluginName:
            self.currentPluginName = pluginName
            self.currentPlugin = self.plugins[pluginName]
            self.filetypes = self.currentPlugin.filetypes

    @pyqtSlot()
    def handleCloseClick(self):
        buttonReply = QMessageBox.warning(self, 
                                          'Close Application', 
                                          'You are about to close the Application,'
                                          ' Press Yes to continue or Cancel to return to the Application',
                                           QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Yes:
            self.exportConfig()
            exit()
        
    @pyqtSlot()
    def selectSrcFiles(self):
        fileDlg = QFileDialog(self, 'Select Files', self.downloadpath, self.filetypes)
        fileDlg.setFileMode(QFileDialog.ExistingFiles)

        if fileDlg.exec_():
            self.filenames = fileDlg.selectedFiles()
            
        self.srcFilesList.clear()
        self.srcFilesList.addItems(self.filenames)
        
    @pyqtSlot()
    def addSrcFiles(self):
        fileDlg = QFileDialog(self, 'Select Files', self.downloadpath, self.filetypes)
        fileDlg.setFileMode(QFileDialog.ExistingFiles)

        if fileDlg.exec_():
            for filename in fileDlg.selectedFiles():
                if filename not in self.filenames:
                    self.filenames.append(filename)
                    self.srcFilesList.addItem(filename)
            
    @pyqtSlot()
    def removeSrcFiles(self):
        selectedModel = self.srcFilesList.selectionModel()
        selected = selectedModel.selectedIndexes()
        for index in selected:
            name = index.data()
            self.filenames.remove(name)
            self.srcFilesList.takeItem(index.row())
        selectedModel.clear()
        
    @pyqtSlot(str)
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
        
    def importConfig(self):
        if os.path.exists(self.configpath):
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
                        if self.config.has_option('Names', 'includedate'):
                            self.includeDate = self.config.getboolean('Names', 'includedate')
                        else:
                            self.includeDate = False
                            
                        if self.config.has_option('Names', 'prefixdate'):
                            self.prefixDate = self.config.getboolean('Names', 'prefixdate')
                        else:
                            self.prefixDate = False
                            
                        if self.config.has_option('Names', 'includeroutes'):
                            self.includeRoutes = self.config.getboolean('Names', 'includeroutes')
                        else:
                            self.includeRoutes = False
                            
                        self.includeRoutes = self.config.getboolean('Names', 'includeroutes')
                    elif section == 'Current':
                        name = self.config['Current']['Current Plugin']
                        if name:
                            self.currentPluginName = name
                        if self.currentPlugin != None:
                            self.filetypes = self.currentPlugin.filetypes

        else:
            self.config.write(self.configpath)
    
    def exportConfig(self):
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
        if self.includeDate:
            self.config.set('Names', 'includedate',  'yes')
        else:
            self.config.set('Names', 'includedate',  'no')
        if self.prefixDate:
            self.config.set('Names', 'prefixdate',  'yes')
        else:
            self.config.set('Names', 'prefixdate',  'no')
        if self.includeRoutes:
            self.config.set('Names', 'includeroutes', 'yes')
        else:
            self.config.set('Names', 'includeroutes', 'no')
        self.config.set('Current', 'Current Plugin', self.currentPluginName)

        with open(self.configpath, 'w') as configfile:
            self.config.write(configfile)
 
class ToExcel:
    
    def __init__(self):
        '''
        '''

    def create_workbook(self, data, savefile):
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
                c = data[row][col]     
                ws[cell] = c
        
        wb.save(savefile)


logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    
    w = ConverterWidget()
    w.show()
    
    sys.exit(app.exec_())
