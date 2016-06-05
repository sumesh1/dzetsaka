# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dzetsaka
                                 A QGIS plugin
 Fast and Easy Classification
                              -------------------
        begin                : 2016-05-13
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Nicolaï Van Lennepkade
        email                : karasiak.nicolas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4 import QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import QgsMessageLog
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
# from dzetsaka_loaddock import dzetsakaDockWidget
# 
import os
from scripts import mainfunction
import tempfile

# load dock 
from ui.dzetsaka_dock import Ui_DockWidget
from ui import filters_dock, historical_dock, help_dock


# Load main widget
class dzetsakaDockWidget(QDockWidget, Ui_DockWidget):
    closingPlugin = pyqtSignal()
    def __init__(self, parent=None):
        super(dzetsakaDockWidget, self).__init__(parent)
        self.setupUi(self)
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

      
class dzetsaka ( QDialog ):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        QDialog.__init__(self)
        sender = self.sender()
        
        # Save reference to the QGIS interface

        legendInterface = self.iface.legendInterface()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'dzetsaka_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&dzetsaka : Classification tool')
          
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'dzetsaka')
        self.toolbar.setObjectName(u'dzetsaka')

        #print "** INITIALIZING dzetsaka"

        self.pluginIsActive = False
        self.dockwidget = None
        
        self.dockwidget = dzetsakaDockWidget()
        
        ## Init to choose file (to load or to save)
        self.dockwidget.outRaster.clear()
        self.dockwidget.outRasterButton.clicked.connect(self.select_output_file)

        self.dockwidget.outModel.clear()
        self.dockwidget.checkOutModel.clicked.connect(self.checkbox_state)
                
        self.dockwidget.inModel.clear()
        self.dockwidget.checkInModel.clicked.connect(self.checkbox_state)

        self.dockwidget.inMask.clear()
        self.dockwidget.checkInMask.clicked.connect(self.checkbox_state)
            
        self.dockwidget.outMatrix.clear()
        self.dockwidget.checkOutMatrix.clicked.connect(self.checkbox_state)
        
        ## init fields   
        self.dockwidget.inField.clear()
        self.dockwidget.inShape.currentIndexChanged[int].connect(self.onChangedLayer)
        
        self.dockwidget.inField.clear()
        # Then we fill it with new selected Layer
        if self.dockwidget.inField.currentText() == '' and self.dockwidget.inShape.currentLayer() and self.dockwidget.inShape.currentLayer()!='NoneType':
            activeLayer = self.dockwidget.inShape.currentLayer()
            provider = activeLayer.dataProvider()
            fields = provider.fields()
            listFieldNames = [field.name() for field in fields]
            self.dockwidget.inField.addItems(listFieldNames)
            
        ## let's run the classification ! 
        self.dockwidget.performMagic.clicked.connect(self.runMagic)
        

    def onChangedLayer(self):
        """!@brief If active layer is changed, change column combobox"""
        # We clear combobox
        self.dockwidget.inField.clear()
        # Then we fill it with new selected Layer
        if self.dockwidget.inField.currentText() == '' and self.dockwidget.inShape.currentLayer() and self.dockwidget.inShape.currentLayer()!='NoneType':
            activeLayer = self.dockwidget.inShape.currentLayer()
            provider = activeLayer.dataProvider()
            fields = provider.fields()
            listFieldNames = [field.name() for field in fields]
            self.dockwidget.inField.addItems(listFieldNames)
        
        

    def select_output_file(self):
        """!@brief Select file to save, and gives the right extension if the user don't put it"""
        sender = self.sender()

        fileName = QFileDialog.getSaveFileName(self.dockwidget, "Select output file","","TIF (*.tif)")
        
        if not fileName:
            return
            
        # If user give right file extension, we don't add it
            
        fileName,fileExtension=os.path.splitext(fileName)
        if sender == self.dockwidget.outRasterButton: 
            if fileExtension!='.tif':
                self.dockwidget.outRaster.setText(fileName+'.tif')
            else:
                self.dockwidget.outRaster.setText(fileName+fileExtension)
        if sender == self.historicalmap.outRasterButton:
            if fileExtension!='.tif':
                self.historicalmap.outRaster.setText(fileName+'.tif')
            else:
                self.historicalmap.outRaster.setText(fileName+fileExtension)
        if sender == self.historicalmap.outShpButton:
            if fileExtension!='.shp':
                self.historicalmap.outShp.setText(fileName+'.shp')
            else:
                self.historicalmap.outShp.setText(fileName+fileExtension)
      
        if sender == self.filters_dock.outRasterButton:
            if fileExtension!='.tif':
                self.filters_dock.outRaster.setText(fileName+'.tif')
            else:
                self.filters_dock.outRaster.setText(fileName+fileExtension)
        
    
    def checkbox_state(self):
        sender=self.sender()
        
        if sender == self.dockwidget.checkInModel and self.dockwidget.checkInModel.isChecked():
            fileName = QFileDialog.getOpenFileName(self.dockwidget, "Select your file","")
            if fileName!='':
                self.dockwidget.inModel.setText(fileName)
                self.dockwidget.inModel.setEnabled(True)
                # Disable training, so disable vector choise
                self.dockwidget.inShape.setEnabled(False)
                self.dockwidget.inField.setEnabled(False)
                
            else:
                self.dockwidget.checkInModel.setChecked(False)
                self.dockwidget.inModel.setEnabled(False)
                self.dockwidget.inShape.setEnabled(True)
                self.dockwidget.inField.setEnabled(True)

        elif sender == self.dockwidget.checkInModel :
            self.dockwidget.inModel.clear()
            self.dockwidget.inModel.setEnabled(False)
            self.dockwidget.inShape.setEnabled(True)
            self.dockwidget.inField.setEnabled(True)

        
        if sender == self.dockwidget.checkOutModel and self.dockwidget.checkOutModel.isChecked():
            fileName = QFileDialog.getSaveFileName(self.dockwidget, "Select output file")
            if fileName!='':
                self.dockwidget.outModel.setText(fileName)
                self.dockwidget.outModel.setEnabled(True)

            else:
                self.dockwidget.checkOutModel.setChecked(False)
                self.dockwidget.outModel.setEnabled(False)
                
        elif sender == self.dockwidget.checkOutModel :
            self.dockwidget.outModel.clear()
            self.dockwidget.outModel.setEnabled(False)

        
        if sender == self.dockwidget.checkInMask and self.dockwidget.checkInMask.isChecked():
            fileName = QFileDialog.getOpenFileName(self.dockwidget, "Select your file")
            if fileName!='':
                self.dockwidget.inMask.setText(fileName)
                self.dockwidget.inMask.setEnabled(True)
            else:
                self.dockwidget.checkInMask.setChecked(False)
                self.dockwidget.inMask.setEnabled(False)
        elif sender == self.dockwidget.checkInMask :
            self.dockwidget.inMask.clear()
            self.dockwidget.inMask.setEnabled(False)
            
        if sender == self.dockwidget.checkOutMatrix and self.dockwidget.checkOutMatrix.isChecked():
            fileName = QFileDialog.getSaveFileName(self.dockwidget, "Save to a *.csv file", "", "CSV (*.csv)")
            
            if fileName!='':
                self.dockwidget.outMatrix.setText(fileName)
                self.dockwidget.outMatrix.setEnabled(True)
                self.dockwidget.inSplit.setEnabled(True)
                self.dockwidget.inSplit.setValue(50)
            else :
                
                self.dockwidget.checkOutMatrix.setChecked(False)
                self.dockwidget.outMatrix.setEnabled(False)
                self.dockwidget.outMatrix.setEnabled(False)
                self.dockwidget.inSplit.setEnabled(False)
                self.dockwidget.inSplit.setValue(100)
                
        elif sender == self.dockwidget.checkOutMatrix :
            self.dockwidget.checkOutMatrix.setChecked(False)
            self.dockwidget.outMatrix.setEnabled(False)
            self.dockwidget.outMatrix.setEnabled(False)
            self.dockwidget.inSplit.setEnabled(False)
            self.dockwidget.inSplit.setValue(100)
        
     
    
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('dzetsaka', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=False,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def loadMenu(self):
        self.menu = QtGui.QMenu(self.iface.mainWindow())
        self.menu.setObjectName("dzetsakaMenu")
        self.menu.setTitle("dzetsaka")
        
        self.menu.main = QAction(QIcon(":/plugins/dzetsaka/img/icon.png"), "dzetsaka classification", self.iface.mainWindow())
        self.menu.addAction(self.menu.main)
        QObject.connect(self.menu.main, SIGNAL("triggered()"),self.loadWidget)
        
        self.menu.addSeparator()
        
        filterMenu = self.menu.addMenu("Filters")

        
        # Filters
        ## Opening
        self.menu.filterOpening = QAction(QIcon(":/plugins/dzetsaka/img/filter.png"), "Opening", self.iface.mainWindow())
        QObject.connect(self.menu.filterOpening, SIGNAL("triggered()"), self.loadFilters)
        filterMenu.addAction(self.menu.filterOpening)

        ## Closing
        self.menu.filterClosing = QAction(QIcon(":/plugins/dzetsaka/img/filter.png"), "Closing", self.iface.mainWindow())
        QObject.connect(self.menu.filterClosing, SIGNAL("triggered()"), self.loadFilters)
        filterMenu.addAction(self.menu.filterClosing)
                
        ## Erosion
        self.menu.filterErosion = QAction(QIcon(":/plugins/dzetsaka/img/filter.png"), "Erosion", self.iface.mainWindow())
        QObject.connect(self.menu.filterErosion, SIGNAL("triggered()"), self.loadFilters)
        filterMenu.addAction(self.menu.filterErosion)

        ## Dilation        
        self.menu.filterDilation = QAction(QIcon(":/plugins/dzetsaka/img/filter.png"), "Dilation", self.iface.mainWindow())
        QObject.connect(self.menu.filterDilation, SIGNAL("triggered()"), self.loadFilters)
        filterMenu.addAction(self.menu.filterDilation)

        ## Separator
        filterMenu.addSeparator()
        
        ## Median
        self.menu.filterMedian = QAction(QIcon(":/plugins/dzetsaka/img/filter.png"), "Median", self.iface.mainWindow())
        QObject.connect(self.menu.filterMedian, SIGNAL("triggered()"), self.loadFilters)
        filterMenu.addAction(self.menu.filterMedian)

        ## Separator
        filterMenu.addSeparator()
        
        ## Historical map
        self.menu.historicalMap = QAction(QIcon(":/plugins/dzetsaka/img/historicalmap.png"), "Historical Map Process", self.iface.mainWindow())
        QObject.connect(self.menu.historicalMap, SIGNAL("triggered()"), self.loadHistoricalMap)
        self.menu.addAction(self.menu.historicalMap)
                    
        # Help
        self.menu.help = QAction(QIcon(":/plugins/dzetsaka/img/icon.png"), "Help", self.iface.mainWindow())
        QObject.connect(self.menu.help, SIGNAL("triggered()"), self.helpPage)
        self.menu.addAction(self.menu.help)
        
        # Add menu
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu)
        
        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        """
        icon_path = ':/plugins/dzetsaka/img/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'dzetsaka : Classification tool'),
            callback=self.loadWidget,
            
            parent=self.iface.mainWindow())
        """
        # add icon to toolbar
        self.add_action(
            ':/plugins/dzetsaka/img/icon.png',
            text=self.tr(u'dzetsaka'),
            callback=self.loadWidget,
            parent=self.iface.mainWindow())
        
        # load default classification widget
        self.loadWidget()
        
        # load dzetsaka menu
        self.loadMenu()
        
    #--------------------------------------------------------------------------
    
    
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING dzetsaka"

        # disconnects
        
        self.dockwidget.closingPlugin.disconnect()

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD dzetsaka"
        """
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&dzetsaka : Classification tool'),
                action)
            
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        """
        self.menu.deleteLater()
        

    #--------------------------------------------------------------------------

    def loadWidget(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            
        #print "** STARTING dzetsaka"

        # dockwidget may not exist if:
        #    first run of plugin
        #    removed on close (see self.onClosePlugin method)
        if self.dockwidget == None:
            # Create the dockwidget (after translation) and keep reference
            self.dockwidget = dzetsakaDockWidget()

        # connect to provide cleanup on closing of dockwidget
        self.dockwidget.closingPlugin.connect(self.onClosePlugin)

        # show the dockwidget
        # TODO: fix to allow choice of dock location
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
            
    
    def loadFilters(self):
        """ """
        self.filters_dock = filters_dock()
        filtersList=['Opening','Closing','Dilation','Erosion','Median']
        self.filters_dock.inFilter.addItems(filtersList)
        
        # make choice
        if self.sender() == self.menu.filterErosion:
            self.filters_dock.inFilter.setCurrentIndex(0)
        elif self.sender() == self.menu.filterClosing:
            self.filters_dock.inFilter.setCurrentIndex(1)
        elif self.sender() == self.menu.filterDilation:
            self.filters_dock.inFilter.setCurrentIndex(2)
        elif self.sender() == self.menu.filterErosion:
            self.filters_dock.inFilter.setCurrentIndex(3)
        elif self.sender() == self.menu.filterMedian:
            self.filters_dock.inFilter.setCurrentIndex(4)

        self.filters_dock.outRaster.clear()
        self.filters_dock.outRasterButton.clicked.connect(self.select_output_file)        
        # show dock
        self.filters_dock.show()
        
        # run Filter
        self.filters_dock.runFilter.clicked.connect(self.runFilter)
        
        
        
            
    def runFilter(self):
        """ """
                #verif before doing the job 
        message=''
        
        try:
            self.filters_dock.inRaster.currentLayer().dataProvider().dataSourceUri()
        except:
            message = "Sorry, you need a raster to make a classification."
        
            
        if message != '':
            QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
        
        # all is ok, so do the job !
        else:
            from scripts.filters import filtersFunction
            
            inRaster=self.filters_dock.inRaster.currentLayer()
            inRaster=inRaster.dataProvider().dataSourceUri()
            
    
            inFilter = self.filters_dock.inFilter.currentText()
            inFilterSize = self.filters_dock.inFilterSize.value()
            inFilterIter = self.filters_dock.inFilterIter.value()
            
            if self.filters_dock.outRaster.text()=='':
               self.outRaster= tempfile.mkstemp('.tif')[1]
            else:
               self.outRaster= self.dockwidget.outRaster.text()
            
            worker = filtersFunction()
            worker.filters(inRaster,self.outRaster,inFilter,inFilterSize,inFilterIter)
            
            self.iface.addRasterLayer(self.outRaster)
             

    
    def loadHistoricalMap(self):
        
        self.historicalmap = historical_dock()
        self.historicalmap.show()
    
        # save raster 
        self.historicalmap.outRasterButton.clicked.connect(self.select_output_file)
        self.historicalmap.outShpButton.clicked.connect(self.select_output_file)
        
        # run
        self.historicalmap.runFilter.clicked.connect(self.runHistoricalMapStep1)
        self.historicalmap.runPostClass.clicked.connect(self.runHistoricalMapStep2)

        self.historicalmap.show()
        
    def runHistoricalMapStep1(self):
        message = ''
        
        try:
            self.historicalmap.inRaster.currentLayer().dataProvider().dataSourceUri()
        except:
            message = "Sorry, you need a raster to make a filter."
        
        if message != '':
            QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
   
        else:
            from scripts.filters import filtersFunction
            
            # load variables 
            
            inRaster = self.historicalmap.inRaster.currentLayer()
            inRaster=inRaster.dataProvider().dataSourceUri()
            
            if self.historicalmap.outRaster.text()=='':
                outRaster = tempfile.mkstemp('.tif')[1]
            else:
                outRaster = self.historicalmap.outRaster.text()
            
            inShapeMedian = self.historicalmap.inMedianSize.value()
            iterMedian = self.historicalmap.inMedianIter.value()
            inShapeGrey = self.historicalmap.inClosingSize.value()
            
            worker = filtersFunction()
            worker.historicalMapFilter(inRaster,outRaster,inShapeGrey,inShapeMedian,iterMedian)
                 
    def runHistoricalMapStep2(self):
        message = ''
        
        try:
            self.historicalmap.inFilteredStep3.currentLayer().dataProvider().dataSourceUri()
        except:
            message = "Sorry, you need a raster to make a filter."
        
        if message != '':
            QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
   
        else:
            from scripts.filters import filtersFunction
            inRaster = self.historicalmap.inFilteredStep3.currentLayer()
            inRaster=inRaster.dataProvider().dataSourceUri()
            
            if self.historicalmap.outShp.text()=='':
                outShp = tempfile.mkstemp('.shp')[1]
            else:
                outShp = self.historicalmap.outShp.text()
            
            sieveSize = self.historicalmap.sieveSize.value()
            inClassNumber = self.historicalmap.classNumber.value()
            
            worker = filtersFunction()
            outRaster = worker.historicalMapPostRaster(inRaster,sieveSize,inClassNumber,outShp)
            outShp = worker.historicalMapPostVector(outRaster,outShp)
            self.iface.addVectorLayer(outShp,os.path.splitext(os.path.basename(outShp))[0],'ogr')
            
            """            
            self.iface.addVectorLayer(outShp,os.path.splitext(os.path.basename(outShp))[0],'ogr')
            self.iface.messageBar().pushMessage("New vector : ",os.path.splitext(os.path.basename(outShp))[0], 3, duration=10)
            """

    def helpPage(self):
        self.helpdock=help_dock()
        self.helpdock.show()
    

    def runMagic(self):
        
        #verif before doing the job 
        message=''
        
        if self.dockwidget.inModel.text()=='':
            try:
                self.dockwidget.inShape.currentLayer().dataProvider().dataSourceUri()
            except:            
                message = "Sorry, if you don't use a model, please specify a vector"
        try:
            self.dockwidget.inRaster.currentLayer().dataProvider().dataSourceUri()
        except:
            message = "Sorry, you need a raster to make a classification."
        
            
        if message != '':
            QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
        
        # all is ok, so do the job !
        else:
            # create temp if not output raster
            if self.dockwidget.outRaster.text()=='':
                outRaster= tempfile.mkstemp()[1]
            else:
                outRaster= self.dockwidget.outRaster.text()
            
            # Get model if given
            
            model=self.dockwidget.inModel.text()
            # if model not given, perform training
            
            inRaster=self.dockwidget.inRaster.currentLayer()
            inRaster=inRaster.dataProvider().dataSourceUri()
            
            inMask=self.dockwidget.inMask.text()
            # check if mask with _mask.extension
                        
            autoMask=os.path.splitext(inRaster)
            autoMask=autoMask[0]+str('_mask')+autoMask[1]
            if os.path.exists(autoMask):
                inMask=autoMask

            if inMask=='':
                inMask=None
            
            # Check if model, else perform training
            if self.dockwidget.inModel.text()!='':
                model=self.dockwidget.inModel.text()
            # Perform training
            else:
                if self.dockwidget.outModel.text()=='':
                    model=tempfile.mkstemp()[1]
                else:
                    model=self.dockwidget.outModel.text()
                
                inShape = self.dockwidget.inShape.currentLayer()
                # Remove layerid=0 from SHP Path
                inShape=inShape.dataProvider().dataSourceUri().split('|')[0]
                
                inField = self.dockwidget.inField.currentText()
                
                inSeed = 0
                if self.dockwidget.checkOutMatrix.isChecked():
                    outMatrix = self.dockwidget.outMatrix.text()
                    inSplit = self.dockwidget.inSplit.value()
                else:
                    inSplit = 1
                    outMatrix = None
                    
                temp=mainfunction.learnModel(inRaster,inShape,inField,model,inSplit,inSeed,outMatrix,inClassifier='GMM')
            
            
            # Perform classification
            try:
                temp=mainfunction.classifyImage()
                temp.initPredict(inRaster,model,outRaster,inMask)
                self.iface.addRasterLayer(outRaster)
            except:
                
                QtGui.QMessageBox.warning(self, 'dzetsaka Magic didn\t work...', 'Something went wrong during the procress, please consult the log in Qgis to have more details.', QtGui.QMessageBox.Ok)       
          