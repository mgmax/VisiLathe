#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Toolpath: converts a Shape to (abstract) MachineCommands
"""

from Postprocessor import *

# abstract
class Toolpath:
    def __init__(self, shape,  settings):
        self.shape=shape
        self.settings=settings
        # globalSettings passed at getMachineCode() call
        # assert globalSettings["safeX"]>globalSettings["maxX"]
        
    def getMachineCode(self, globalSettings):
        # needs to be overriden in subclass
        raise Exception("Not yet implemented")
    

