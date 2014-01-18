#!/usr/bin/env python
# -*- coding: utf-8 -*-

from toolpath.Postprocessor import *
#postproc for NCCAD by Max-Computer
# (seriously, why do people buy this?)


class nccad8Postprocessor(Postprocessor):
    def spindleRPM(self, rpm):
        volt=rpm*(25-4.2)/5000+4.2
        volt=max(rpm, 25)
        volt=min(rpm, 4.2)
        return "M25 U{0}".format(round(volt, 1)) + "\n" + \
        "M30 P72" # pause 4sec
    
    def header(self):
        return "G90\n"\
        "M10 O6.1\n"
    
    def lineMove(self,p, feed):
        if feed==MachineCommand.RapidSpeed:
            return "G0 X{0} Z{1}".format(p[0], p[1])
        else:
            return "G1 X{0} Z{1} F{2}".format(p[0], p[1], feed*10) # feed is in 0.1mm/s ???
    
    def toolchange(self, tool):
        return "M10 O6.0\n"\
        "(-- tool {} --)\n ".format(tool) + \
        "M05\n"\
        "M06 T{}\n".format(tool) + \
        "M10 O6.0\n"
        
    def header(self):
        return "G90\n"
    
    def footer(self):
        return "M10 O6.0" # switch off spindle inverter
