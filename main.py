#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main GUI file

For developing and running this software you need: PyQt4
debian/ubuntu packages: python-qt4  pyqt4-dev-tools python-qt4-doc

For compiling:
run ./ui/compileAll.py


Documentation see:

PyQt Docs:
Specific objects like QButton: http://pyqt.sourceforge.net/Docs/PyQt4/classes.html -> search for name of the class you're looking for
General stuff: http://pyqt.sourceforge.net/Docs/PyQt4/

python "cheatsheet" (still looking for a better one):
http://rgruet.free.fr/PQR27/PQR2.7.html



"""


import sys
import pickle # (de)serialisation

# QT GUI stuff
from PyQt4.QtGui import *
#from PyQt4.QtCore import pyqtSignature

from ui import *
from ParameterHelper import *
from ZParallelToolpath import *
from ui.PreviewWidget import *

class VisiLatheGUI(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    
    # constants:
    INDEX_DRAWINGS=1
    INDEX_TOOLPATHS=2
    INDEX_SIMULATION=3
    FILE_STRUCTURE_VERSION="2013-12-25" # increment this as soon as the file format is incompatible with earlier versions
        
    
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        
        self.setupUi(self)
        self.ignoreValueEvents=False
        
        
        # Signal-Slot-connections
        self.workflowTabs.currentChanged.connect(self.workflowTabChanged)
        self.toolpathList.itemSelectionChanged.connect(self.toolpathSelectionChanged)
        self.toolpathAddButton.clicked.connect(self.addToolpath)
        self.toolpathRemoveButton.clicked.connect(self.removeSelectedToolpath)
        # unselect toolpath (and auto-close the settings) when pressing "OK" in the settings dialog
        self.toolpathSettingsButtonGroup.clicked.connect(self.unselectToolpaths)
        self.selectNCFileButton.clicked.connect(self.selectNCFile)
        self.saveNCButton.clicked.connect(self.saveNCFile)
        self.simSlider.valueChanged.connect(self.simSliderChanged)
        self.simSpeedSlider.valueChanged.connect(self.simSpeedSliderChanged)
        self.runSimButton.clicked.connect(self.runPauseSimulation)
        
        self.simTimer=QTimer()
        self.simTimer.setInterval(100)
        self.simTimer.timeout.connect(self.simulationTick)
        
        # init
        # parameter name, object, default value, type
        # (type currently unused)
        self.globalSettingsParameters=[{"name":"materialDiameter", "object":self.materialDiameterSpinBox, "default":0, "type": float}, 
                              {"name":"materialLength", "object":self.materialLengthSpinBox, "default": 0, "type": float},
                              {"name":"flightDistance", "object":self.flightDistanceSpinBox, "default": 20, "type": float}, 
                              {"name":"approachDistance", "object":self.safeApproachSpinBox, "default": 2, "type": float}, 
                              {"name":"curveTolerance", "object":self.curveToleranceSpinBox, "default": 0.010, "type": float}, 
                              ]
        self.toolpathSettingsParameters=[{"name":"name", "object":self.toolpathNameLineEdit, "default":"Unnamed Toolpath", "type": str},
                                         {"name":"tool", "object":self.toolSpinBox, "default":0, "type": int},
                                         {"name":"feedValue", "object":self.feedSpinBox, "default":10, "type": float},
                                         {"name":"feedMode", "object":self.feedModeComboBox, "default":0, "type": "enum"},
                                         {"name":"speedValue", "object":self.speedSpinBox, "default":2000, "type": float},
                                         {"name":"speedMode", "object":self.speedModeComboBox, "default":0, "type": "enum"}, 
                                          {"name":"cutDepth", "object":self.cutDepthSpinBox, "default": 0.5, "type": float}, 
                                          {"name":"finalPassDepth", "object":self.finalPassSpinBox, "default": 0.2, "type": float}
                                         # {"name":"", "object":, "default":, "type": },
                                         ]
                                         
        # connect all changes of GUI settings elements to updateValuesFromGUI():
        for s in self.globalSettingsParameters + self.toolpathSettingsParameters:
            if hasattr(s["object"], 'valueChanged'):
                s["object"].valueChanged.connect(self.updateValuesFromGUI)
            elif hasattr(s["object"], 'currentIndexChanged'):
                s["object"].currentIndexChanged.connect(self.updateValuesFromGUI)
            elif hasattr(s["object"], 'textEdited'):
                s["object"].textEdited.connect(self.updateValuesFromGUI)
            else:
                raise Exception("could not connect unknown GUI-Object "+str(s["object"])+" to self.updateValuesFromGUI")
        
        
        self.loadEmptyFile()
        self.workflowTabChanged(0)
        
    ####################################################################################
    # Main GUI
    ####################################################################################

    def about(self):
        QMessageBox.information(self, "VisiLathe", "VisiLathe (C) 2013 VisiLathe Contributors.\nPatrick Kanzler, Max Gaukler\nhttp://github.com/mgmax/VisiLathe\n\nLicensed under GNU GPL 2, see the file COPYING in the program directory")
    
    def workflowTabChanged(self, index):
        # The "workflow" tabs at the left were switched to another step
        # Change the rest of the GUI accordingly
        
        # tab indices - need to be readjusted when other tabs are added

        
        # show/hide the additional settings GroupBox
        self.drawingSettings.setVisible(index==self.INDEX_DRAWINGS)
        self.resetSimulation()
        self.toolpathSelectionChanged()
        
    def workflowNext(self):
        # switch to next workflow tab
        self.workflowTabs.setCurrentIndex(self.workflowTabs.currentIndex()+1)
    
    def updatePreview(self):
        self.previewWidget.setMaterialSize(self.globalSettings["materialLength"], self.globalSettings["materialDiameter"])
        c=[]
        for t in self.toolpaths:
            c.extend(t.getMachineCode(self.globalSettings))
        self.previewWidget.showMachineCode(c)
        self.simSlider.setMaximum(len(c))
        self.simSlider.setValue(len(c))
        self.simSliderChanged()
    
    ####################################################################################
    # settings handling
    ####################################################################################
    
    # GUI -> globalSettings, toolpathSettings
    def updateValuesFromGUI(self):
        if self.ignoreValueEvents:
            return
        self.globalSettings=ParameterHelper.getValuesFromGUI(self.globalSettingsParameters)
        if self.currentToolpath is not None:
            self.currentToolpath.settings=ParameterHelper.getValuesFromGUI(self.toolpathSettingsParameters)
        self.loadToolpathsInGUI()        
        self.updatePreview()
    
    
    # globalSettings, toolpathSettings -> GUI
    def loadValuesInGUI(self):
        if self.ignoreValueEvents:
            return
        self.ignoreValueEvents=True
        ParameterHelper.setValuesInGUI(self.globalSettingsParameters, self.globalSettings)    
        if self.currentToolpath is not None:
            ParameterHelper.setValuesInGUI(self.toolpathSettingsParameters, self.currentToolpath.settings)
        self.loadToolpathsInGUI()
        self.updatePreview()
        self.ignoreValueEvents=False
    
    ####################################################################################
    # DRAWING
    ####################################################################################
    
    
    # TODO TODO TODO 
    
    
    
    ####################################################################################
    # TOOLPATH
    ####################################################################################
    
    # toolpath array -> GUI
    def loadToolpathsInGUI(self):
        oldIgnoreValueEvents=self.ignoreValueEvents
        self.ignoreValueEvents=True
        self.toolpathList.clear()
        for t in self.toolpaths:
            self.toolpathList.addItem(t.settings["name"])
        # restore selection
        if self.currentToolpath in self.toolpaths:
            self.toolpathList.setItemSelected(self.toolpathList.item(self.toolpaths.index(self.currentToolpath)), True)
        else:
            self.currentToolpath = None # current toolpath was deleted
        self.ignoreValueEvents=oldIgnoreValueEvents
        self.toolpathSelectionChanged()
    
    def unselectToolpaths(self):
        for i in self.toolpathList.selectedItems():
            self.toolpathList.setItemSelected(i, False)
    
    # show/hide the toolpath settings GroupBox
    def toolpathSelectionChanged(self):
        if self.ignoreValueEvents:
            return
#        print self.toolpathList.currentRow()
#        print self.toolpathList.selectedItems()
        self.toolpathSettings.setVisible(self.workflowTabs.currentIndex()==self.INDEX_TOOLPATHS and len(self.toolpathList.selectedItems())>0)
        if len(self.toolpathList.selectedItems())>0:
            self.currentToolpath=self.toolpaths[self.toolpathList.currentRow()]
        else:
            self.currentToolpath=None
        self.loadValuesInGUI() # necessary?
        self.toolpathRemoveButton.setDisabled(len(self.toolpathList.selectedItems())==0)
        
    def addToolpath(self):
        defaultSettings={}
        for s in self.toolpathSettingsParameters:
            defaultSettings[s["name"]]=s["default"]
        t=ZParallelToolpath(shape=CylinderShape(30, 50, 15), settings=defaultSettings)
        self.toolpaths.append(t)
        self.currentToolpath=t
        # TODO selection of different toolpath types
        # TODO default settings for toolpath: specific for toolpathtype....
        self.loadToolpathsInGUI()
        self.toolpathSelectionChanged()
        self.loadValuesInGUI()
        self.toolpathNameLineEdit.selectAll()
        self.toolpathNameLineEdit.setFocus()
    
    def removeSelectedToolpath(self):
        if len(self.toolpathList.selectedItems())==0:
            return
        self.toolpaths.pop(self.toolpathList.currentRow())
        self.loadToolpathsInGUI()
        self.loadValuesInGUI()
        
    
    ####################################################################################
    # Simulation
    ####################################################################################
    
    def resetSimulation(self):
        self.simTimer.stop()
        self.simSlider.setValue(self.simSlider.maximum())
        self.runSimButton.setChecked(False)
        self.simSliderChanged()
        
    def runPauseSimulation(self):
        if self.simTimer.isActive():
            self.simTimer.stop()
            self.runSimButton.setChecked(False)
        else:
            # not running: start
            if self.simSlider.value()==self.simSlider.maximum():
                # if at end, rewind to start
                self.simSlider.setValue(0)
            self.runSimButton.setChecked(True)
            self.simSpeedSliderChanged() # initialize timer period
            self.simTimer.start()
            
    
    def simulationTick(self):
        # increment simulation slider, this causes an event that updates the preview
        self.simSlider.setValue(self.simSlider.value()+1)
        if self.simSlider.value()==self.simSlider.maximum():
            self.resetSimulation()
            
    def simSliderChanged(self):
        self.previewWidget.setPreviewStep(self.simSlider.value())
        self.simProgressLabel.setText("{0}/{1}".format(self.simSlider.value(), self.simSlider.maximum()))
    
    def simSpeedSliderChanged(self):
        self.simTimer.setInterval(1000/self.simSpeedSlider.value())
        if self.simTimer.isActive():
            self.simTimer.start() # restart with new interval
    
    ####################################################################################
    # Save/Open Project
    ####################################################################################
    def loadEmptyFile(self):
        self.globalSettings={}
        for s in self.globalSettingsParameters:
            self.globalSettings[s["name"]]=s["default"]
        self.NCFilename=""
        self.projectFilename=""
        self.currentToolpath=None
        self.toolpaths=[]
        self.loadValuesInGUI()
        self.workflowTabs.setCurrentIndex(0)
        
    def newProject(self):
        # TODO check for unsaved changes?
        self.loadEmptyFile()
        self.statusbar.showMessage("Successfully loaded empty project.", 5000)
        
    def saveProjectAs(self):
        f = QFileDialog.getSaveFileName(self, "Save Project As...",
                                self.projectFilename,
                                "VisiLathe Project (*.visilathe)")
        self.projectFilename=f
        self.saveProject()
    
    def saveProject(self):
        try:
            f=file(self.projectFilename, "w")
            # ATTENTION: increment FILE_STRUCTURE_VERSION on every incompatible data format change
            data={"fileStructureVersion":self.FILE_STRUCTURE_VERSION, "globalSettings":self.globalSettings, "toolpaths":self.toolpaths}
            pickle.dump(data, f)
            f.close()
            QMessageBox.warning(self, "Warning","There is currently no guarantee that projects can be opened in future versions of VisiLathe! The file format is likely to change and there won't be any backwards compatibility.")
            self.statusbar.showMessage("Successfully saved project.", 5000)
        except Exception, e:
            # TODO better messages
            QMessageBox.critical(self, "Error saving file", e.__repr__() + "\n\n" + str(e))
            
    def openProject(self):
        try:
            # TODO ask for "save changes"
            self.loadEmptyFile()
            filename=QFileDialog.getOpenFileName(self, "Open Project",
                                self.projectFilename,
                                "VisiLathe Project (*.visilathe)")
            f=file(filename, "r")
            data=pickle.load(f)
            self.globalSettings=data["globalSettings"]
            # TODO better solution for different toolpath-types
            # we can't just import the whole object because it also contains the functions that may have changed
            self.toolpaths=[]
            for t in data["toolpaths"]:
                # TODO load shape
                self.toolpaths.append(ZParallelToolpath(shape=CylinderShape(30, 50, 15), settings=t.settings))
            assert data["fileStructureVersion"]==self.FILE_STRUCTURE_VERSION
            self.loadValuesInGUI()
            self.statusbar.showMessage("Successfully loaded project.", 5000)

            
        except Exception, e:
            # TODO better messages
            QMessageBox.critical(self, "Error loading file", e.__repr__() + "\n\n" + str(e))
            
        

    
    ####################################################################################
    # NC File
    ####################################################################################
    
    # TODO: Postprocessor selection
    # TODO Postproc settings, CRLF etc
    # TODO disable savebutton before a file is selected
    def selectNCFile(self):
        f = QFileDialog.getSaveFileName(self, "Save File",
                            self.NCFilename,
                            " ")
        self.NCFilenameLabel.setText(f)
        self.NCFilename=f
    
    def saveNCFile(self):
        # TODO ask for overwriting here, but not at selectNCFile?
        try:
            f=file(self.NCFilename, "w")
            p=Postprocessor()
            code=[]
            for t in self.toolpaths:
                for c in t.getMachineCode(self.globalSettings):
                    code.append(c)
            for l in p.createCode(code, settings=None):
                f.write(l)
            f.close()
        except Exception, e:
            # TODO better messages
            QMessageBox.critical(self, "Error", e.__repr__() + "\n\n" + str(e))


def main():    
    app = QtGui.QApplication(sys.argv)
    gui = VisiLatheGUI()
    gui.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
