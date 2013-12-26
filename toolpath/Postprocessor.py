#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Postprocessor: converts machine commands to the machine's GCode dialect
"""

from MachineCommand import *

class Postprocessor:
    def createCode(self, commands, settings):
        lastTool=None
        yield self.header()
        
        for c in commands:
            if isinstance(c, MachineCommand.LineMove):
                for p in c.points:
                    yield self.lineMove(p, c.feed)
                    
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
        "asdf n"
        
    
    def footer(self):
        return "\nTODO END\n"\
        "asdf n"
    
    def toolchange(self, tool):
        return "TODO M6 T{0}".format(tool)
    
    def spindleRPM(self, rpm):
        return "TODO Spindeldrehzahl {0}".format(rpm)
    
    def lineMove(self,p, feed):
        if feed==MachineCommand.RapidSpeed:
            return "G0 X{0} Z{1}".format(p[0], p[1])
        else:
            return "G1 X{0} Z{1} F{2}".format(p[0], p[1], feed)
        

if __name__ == '__main__':
    print "Testing postproc"
    p=Postprocessor()
    points=[(0, 1), (0, 2.23456), (1, 2)]
    b=MachineCommand.BlockStart("Schruppen", 3, 2000, 20)
    m=MachineCommand.LineMove(points, 123)
    commands=[b, m]
    for i in p.createCode(commands, None):
        print i
    
