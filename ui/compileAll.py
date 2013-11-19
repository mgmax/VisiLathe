#!/usr/bin/env python

# based on code from FabLab-Kassensystem, heavily modified

from PyQt4 import uic
import fnmatch
import os
import subprocess
currentDir=os.path.dirname(__file__)+"/"
os.chdir(currentDir)
currentDir="./"
for file in os.listdir(currentDir):
    if (file.endswith(".ui")): # UI (Qt Designer) file
        print file
        uic.compileUi(file, open(currentDir + "Ui_" + file[:-2] + 'py', "w"), execute=True)
    if file.endswith(".qrc"): # QRC (image resource) file
        print file
        subprocess.call(["pyrcc4", currentDir + file, "-o",  currentDir + file[:-4] + '_rc.py'])
