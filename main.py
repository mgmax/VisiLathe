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
        self.workflowTabChanged(0)
        
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
