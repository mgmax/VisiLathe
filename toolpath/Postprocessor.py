#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Postprocessor: converts machine commands to the machine's GCode dialect
"""

from MachineCommand import *
import importlib

class Postprocessor:
    @staticmethod
    def listPostprocessors():
        return ["generic", "nccad8"] # TODO get from directory listing ../machine/
    
    @staticmethod
    def getFromName(name):
        m = importlib.import_module("machine."+name, "..") # load python file from ../machine/
        c = getattr(m, name+"Postprocessor") # get class
        return c
    
    def __init__(self, globalSettings):
        self.globalSettings=globalSettings
    
    def createCode(self, commands):
        lastTool=None
        yield self.header()
        
        for c in commands:
            if isinstance(c, MachineCommand.LineMove):
                for p in c.points:
                    x=p[0]
                    z=p[1]
                    [x, z]=self.transformCoordinates(x, z)
                    if self.useDiameterMode():
                        x=x*2
                    yield self.lineMove([x, z], c.feed)
                    
            elif isinstance(c, MachineCommand.BlockStart):
                yield ""
                yield "(------ start block {0} ------)".format(c.blockName)
                
                if c.tool != lastTool:
                    # toolchange
                    yield self.toolchange(c.tool)
                    lastTool=c.tool
                
                yield self.spindleRPM(c.rpm)
                
            else:
                raise Exception("Unknown MachineCommand object " + str(c))
                
        yield self.footer()
    
    def header(self):
        return "TODO INIT\n"\
        "asdf n"\
        "G90"
        
    
    def footer(self):
        return "\nTODO END\n"\
        "asdf n"
    
    def toolchange(self, tool):
        return "TODO M6 T{0}".format(tool)
    
    def spindleRPM(self, rpm):
        return "TODO Spindeldrehzahl {0}".format(rpm)
    
    def lineMove(self,p, feed):
        if feed==MachineCommand.RapidSpeed:
            return "G0 "+self.formatCoordinate(p)
        else:
            return "G1 {0} F{1}".format(self.formatCoordinate(p), feed)
    def formatCoordinate(self, p):
        return "X{:.2} Z{:.2}".format(p)
        return 
    
    def useDiameterMode(self):
        return True
    
    def transformCoordinates(self, x, z):
        return [x, z-self.globalSettings["materialLength"]]

if __name__ == '__main__':
    print "Testing postproc"
    p=Postprocessor()
    points=[(0, 1), (0, 2.23456), (1, 2)]
    b=MachineCommand.BlockStart("Schruppen", 3, 2000, 20)
    m=MachineCommand.LineMove(points, 123)
    commands=[b, m]
    for i in p.createCode(commands, None):
        print i
    
