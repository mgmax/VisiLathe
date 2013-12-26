#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
import math

class Shape:
    def maxX(self, z):
        raise Exception("Not yet implemented")
    def getZLimits(self):
        raise Exception("Not yet implemented")

class DemoShape(Shape):
    
    def __init__(self, points):
        points=[]
        for i in numpy.arange(30, 60, 0.1):
            points.append((20*math.sin(i)+30, i))
        self.points=points
            
    def maxX(self, zRequested):
        # get highest X value at requested z
        if len(self.points)<2:
            return None
        lastZ=self.points[0][1]
        lastX=self.points[0][1]
        maxX=None
        for p in self.points:
            (x, z)=p
            if lastZ <= zRequested and z>=zRequested:
                # we crossed the requested z value
                deltaZ=z-lastZ
                deltaZRequested=z-zRequested # how far are we away from the requested Z value
                if deltaZ==0:
                    # vertical line
                    interpolatedX=max(x, lastX)
                else:
                    # non-vertical line: interpolate linearly
                    factor=deltaZRequested/deltaZ # factor=0 for z=zRequested ... factor=1 for zLast=zRequested
                    assert factor >= 0
                    assert factor <= 1
                    interpolatedX = lastX*factor + x*(1-factor)
                maxX=max(maxX, interpolatedX)
            lastZ=z
            lastX=x
        return maxX
    
    def getZLimits(self):
        assert len(self.points)>0
        zMin=self.points[0][1]
        zMax=self.points[0][1]
        for p in self.points:
            (x, z)=p
            zMin=min(zMin, z)
            zMax=max(zMax, z)
        return [zMin, zMax]


class CylinderShape(Shape):
    def __init__(self, zMin, zMax, x):
        self.zMin=zMin
        self.zMax=zMax
        self.x=x
    def maxX(self, z):
        if z>=self.zMin and z<=self.zMax:
            return self.x
        else:
            return None
    def getZLimits(self):
        return [self.zMin, self.zMax]



if __name__ == '__main__':
    pass
    
