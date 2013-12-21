#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Toolpath: converts a Shape to (abstract) MachineCommands
"""

from Postprocessor import *

# abstract
class Toolpath:
    def __init__(self, shape,  settings, globalSettings):
        self.shape=shape
        self.settings=settings
        self.globalSettings=globalSettings
        assert globalSettings["safeX"]>globalSettings["maxX"]
        
    def getMachineCode(self):
        # needs to be overriden in subclass
        raise Exception("Not yet implemented")
    

