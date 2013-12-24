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

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature

from ui import *
from ParameterHelper import *
import sys

class VisiLatheGUI(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        
        self.setupUi(self)
        
        # Signal-Slot-connections
        self.workflowTabs.currentChanged.connect(self.workflowTabChanged)
        

        # init
        self.globalSettings={}
        # parameter name, object, default value, type
        # (type currently unused)
        self.globalSettingsParameters=[{"name":"materialDiameter", "object":self.materialDiameterSpinBox, "default":0, "type": float}, 
                              {"name":"materialLength", "object":self.materialLengthSpinBox, "default": 0, "type": float},
                              {"name":"flightDistance", "object":self.flightDistanceSpinBox, "default": 20, "type": float}, 
                              {"name":"approachDistance", "object":self.safeApproachSpinBox, "default": 2, "type": float}
                              ]
        self.toolpathSettingsParameters=[{"name":"name", "object":self.toolpathNameLineEdit, "default":"Unnamed Toolpath", "type": str},
                                         {"name":"tool", "object":self.toolSpinBox, "default":0, "type": int},
                                         {"name":"feedValue", "object":self.feedSpinBox, "default":10, "type": float},
                                         {"name":"feedMode", "object":self.feedModeComboBox, "default":0, "type": "enum"},
                                         {"name":"speedValue", "object":self.speedSpinBox, "default":2000, "type": float},
                                         {"name":"speedMode", "object":self.speedModeComboBox, "default":0, "type": "enum"}
                                         # {"name":"", "object":, "default":, "type": },
                                         ]
                                         
        # connect all changes of GUI settings elements to updateValues():
        for s in self.globalSettingsParameters + self.toolpathSettingsParameters:
            if hasattr(s["object"], 'valueChanged'):
                s["object"].valueChanged.connect(self.updateValues)
            elif hasattr(s["object"], 'currentIndexChanged'):
                s["object"].currentIndexChanged.connect(self.updateValues)
            elif hasattr(s["object"], 'textEdited'):
                s["object"].textEdited.connect(self.updateValues)
            else:
                raise Exception("could not connect unknown GUI-Object "+str(s["object"])+" to self.updateValues")
        self.loadDefaultValues()
        
        # connect events *after* loadDefaultValues
        
        
        self.workflowTabChanged(0)
        
        
        # TODO als nächstes zu tun: toolpathList zum Leben erwecken, als Shape erstmal immer das CylinderShape nutzen. Dann toolpathSettings mit einbinden
    
    def updateValues(self):
        if self.ignoreValueEvents:
            return
        self.globalSettings=ParameterHelper.getValuesFromGUI(self.globalSettingsParameters)
        print self.globalSettings
        # TODO toolpath stuff
    
    def loadDefaultValues(self):
        for s in self.globalSettingsParameters:
            self.globalSettings[s["name"]]=s["default"]
        self.currentToolpath=None
        self.loadValues()
    
    def loadValues(self):
        if self.ignoreValueEvents:
            return
        self.ignoreValueEvents=True
        ParameterHelper.setValuesInGUI(self.globalSettingsParameters, self.globalSettings)
        # TODO toolpath settings stuff
        self.ignoreValueEvents=False
        
    def workflowTabChanged(self, index):
        # The "workflow" tabs at the left were switched to another step
        # Change the rest of the GUI accordingly
        
        # tab indices - need to be readjusted when other tabs are added
        INDEX_DRAWINGS=1
        INDEX_TOOLPATHS=2
        
        # TODO abort editing / ask for unsaved changes
        
        # show/hide the additional settings GroupBox
        self.toolpathSettings.setVisible(index==INDEX_TOOLPATHS)
        self.drawingSettings.setVisible(index==INDEX_DRAWINGS)
        
    def workflowNext(self):
        # switch to next workflow tab
        self.workflowTabs.setCurrentIndex(self.workflowTabs.currentIndex()+1)

def main():    
    app = QtGui.QApplication(sys.argv)
    gui = VisiLatheGUI()
    gui.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
