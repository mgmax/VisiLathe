#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Postprocessor import *
#postproc for NCCAD by Max-Computer
# (seriously, why do people buy this?)


class NccadPostprocessor(Postprocessor):
    def spindleRPM(self, rpm):
        volt=rpm*(25-4.2)/5000+4.2
        volt=max(rpm, 25)
        volt=min(rpm, 4.2)
        return "M25 U{0}".format(round(volt, 1))
        return "M30 P72" # pause 4sec
    
    def toolchange(self, tool):
        return "TODO M6 T{0}".format(tool)
        
    def header(self):
        return "M10 O6.1" # switch on spindle inverter
    
    def footer(self):
        return "M10 O6.0" # switch off spindle inverter
