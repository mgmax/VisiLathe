#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO translate to English
Längsdrehen: 
"""
from MachineCommand import *
from Postprocessor import *
from Toolpath import *
from drawing import *
from numpy import *


class ZParallelToolpath(Toolpath):
    def getMachineCode(self, globalSettings): 
        zDirection = self.settings.get("zDirection", 0)
        zDirection= 1 if (zDirection>0) else -1
        #zResolution=self.settings.get("zResolution", 0.1)
        zResolution=globalSettings["curveTolerance"] # TODO extra setting
        
        maxX=globalSettings["materialDiameter"]/2
        # TODO minX not unused, no GUI option
        minX=0
        #minX=self.settings.get("minX", globalSettings["minX"])
        safeX=maxX + globalSettings["flightDistance"]
        cutDepth=self.settings["cutDepth"]
        finalPassDepth=self.settings["finalPassDepth"]
        approachDistance=self.settings.get("approachDistance", globalSettings["approachDistance"])
        
        # TODO FeedMode/SpeedMode
        assert self.settings["speedMode"]==0
        assert self.settings["feedMode"]==0
        
        yield MachineCommand.BlockStart(blockName=self.settings["name"], tool=self.settings["tool"], rpm=self.settings["speedValue"], feed=self.settings["feedValue"])

        # z limits
        [zShapeMin, zShapeMax]=self.shape.getZLimits()
        zMin=self.settings.get("zMin", zShapeMin)
        zMax=self.settings.get("zMax", zShapeMax)
        assert(zMin<=zMax)
        
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
        numCuts=math.ceil(abs((maxX-minX)/cutDepth))
        if numCuts==0:
            return
        elif numCuts==1:
            xLayers=[minX]
        else:
            [xLayers, realCutDepth]=linspace(max(maxX-cutDepth,minX),minX,num=numCuts,retstep=True) # TODO rewrite this line, I don't understand it anymore
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
            yield MachineCommand.LineMove([(safeX, points[0][1])], MachineCommand.RapidSpeed)
            # rapid down to approach position above startpoint
            yield MachineCommand.LineMove([(points[0][0]+cutDepth+approachDistance, points[0][1])], MachineCommand.RapidSpeed) # TODO correct approach offset
            # slow movement: approach and cut
            c=MachineCommand.LineMove(points, self.settings["feedValue"]) # TODO extra feed for x approach/plunge
            c.simplify(tolerance=globalSettings["curveTolerance"])
            yield c
            # rapid out to safe position above endpoint
            yield MachineCommand.LineMove([(safeX, points[-1][1])], MachineCommand.RapidSpeed)
        
        # roughingPasses
        for xLimit in  xLayers:
            for c in cutOneLayer(self, xLimit,  offset=finalPassDepth):
                yield c
                
        # final pass
        for c in cutOneLayer(self, xLimit=minX, offset=0):
            yield c
        


        

if __name__ == '__main__':
    t=ZParallelToolpath(shape=CylinderShape(30, 50, 15), \
                   settings={"name":"Beispiel", "tool":3, "speedMode":0, "speedValue":3000, "feedValue":100,  "feedMode":0, "zDirection":+1, "cutDepth":1, "finalPassDepth":0.2})
    code=[]
    for c in t.getMachineCode(globalSettings={"materialDiameter":60, "flightDistance":5, "approachDistance": 1, "curveTolerance":0.001}):
        print c
        code.append(c)
    
    p=Postprocessor()
    for l in p.createCode(code, settings=None):
        print l
