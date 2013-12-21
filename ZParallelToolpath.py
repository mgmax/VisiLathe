#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO translate to English
Längsdrehen: 
"""
from MachineCommand import *
from Postprocessor import *
from Toolpath import *
from Shape import *
from numpy import *


class ZParallelToolpath(Toolpath):
    def getMachineCode(self): 
        zDirection = self.settings.get("zDirection", 0)
        zDirection= 1 if (zDirection>0) else -1
        zResolution=self.settings.get("zResolution", 1)
        
        maxX=self.settings.get("maxX", self.globalSettings["maxX"])
        minX=self.settings.get("minX", self.globalSettings["minX"])
        cutDepth=self.settings["cutDepth"]
        finalPassDepth=self.settings["finalPassDepth"]
        approachDistance=self.settings.get("approachDistance", self.globalSettings["approachDistance"])
        
        yield MachineCommand.BlockStart(blockName=self.settings["name"], tool=self.settings["tool"], rpm=self.settings["rpm"], feed=self.settings["feed"])

        # z limits
        [zShapeMin, zShapeMax]=self.shape.getZLimits()
        zMin=self.settings.get("zMin", zShapeMin)
        zMax=self.settings.get("zMax", zShapeMax)
        
        # discretized z range
        zPoints=arange(zMin, zMax, zResolution)
        if zDirection==-1:
            zPoints=zPoints[::-1] # reverse array
        
        n=len(zPoints)
        if n<2:
            raise Exception("empty z range")
        
        # how does the stock material look like?
        # TODO use data from earlier toolpaths
        xMaterialRemaining=ones(len(zPoints))*maxX
        
        # shape to be cut
        xShape=copy(xMaterialRemaining)
        for i in range(n):
            x=self.shape.maxX(zPoints[i])
            if x is None:
                x=xMaterialRemaining[i] # TODO plus offset? adding an offset would introduce "sharp edges" in some cases
            xShape[i]=x
        
        
        # roughing passes
        # slightly reduce cutDepth so that we have evenly spaced "layers" from maxX down to minX, including minX
        [xLayers, realCutDepth] = linspace(max(maxX-cutDepth,minX),minX,num=math.ceil((maxX-minX)/cutDepth),retstep=True)
        assert realCutDepth <= cutDepth
        
        def cutOneLayer(self, xLimit,  offset):
            # for each depth:
            materialRemoved=False
            points=[]
            for i in range(n): # for each point
                # determine X: use the shape, except if lower than the currently cut depth
                x=xShape[i]+offset
                if x < xLimit: # do not (at once) cut deeper than the cut depth
                    x=xLimit
                if x < xMaterialRemaining[i]:
                    materialRemoved=True
                    xMaterialRemaining[i]=x
                points.append((x, zPoints[i]))
            if not materialRemoved:
                return # skip empty block
            # rapid to safe position above startpoint
            yield MachineCommand.LineMove([(self.globalSettings["safeX"], points[0][1])], MachineCommand.RapidSpeed)
            # rapid down to approach position above startpoint
            yield MachineCommand.LineMove([(points[0][0]+cutDepth+approachDistance, points[0][1])], MachineCommand.RapidSpeed) # TODO correct approach offset
            # slow movement: approach and cut
            c=MachineCommand.LineMove(points, self.settings["feed"]) # TODO extra feed for x approach/plunge
            c.simplify(tolerance=self.globalSettings["curveTolerance"])
            yield c
            # rapid out to safe position above endpoint
            yield MachineCommand.LineMove([(self.globalSettings["safeX"], points[-1][1])], MachineCommand.RapidSpeed)
        
        # roughingPasses
        for xLimit in  xLayers:
            for c in cutOneLayer(self, xLimit,  offset=finalPassDepth):
                yield c
                
        # final pass
        for c in cutOneLayer(self, xLimit=minX, offset=0):
            yield c
        


        

if __name__ == '__main__':
    t=ZParallelToolpath(shape=CylinderShape(30, 50, 15), \
                   settings={"name":"Beispiel", "tool":3, "rpm":3000, "feed":"100", "zDirection":+1, "cutDepth":1, "finalPassDepth":0.2}, \
                   globalSettings={"maxX":20, "minX":0, "safeX":25, "approachDistance": 1, "curveTolerance":0.001})
    code=[]
    for c in t.getMachineCode():
        print c
        code.append(c)
    
    p=Postprocessor()
    for l in p.createCode(code, settings=None):
        print l
