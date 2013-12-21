#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Shape:
    def maxX(self, z):
        raise Exception("Not yet implemented")
    def getZLimits(self):
        raise Exception("Not yet implemented")

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
