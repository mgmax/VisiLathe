#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MachineCommand:
    RapidSpeed="rapid" # pseudo-object
    
    class LineMove:
        def __init__(self, points, feed):
            self.points=points
            self.feed=feed
        
        def simplify(self, tolerance):
            if len(self.points)<2:
                return
                
            # first pass: remove points that are exactly in a flat horizontal or vertical line between other points
            def isBetween(a, b, c):
                return (a<=b and b<=c) or (c<=b and b<=a)
            newPoints=[self.points[0]]
            for i in range(1, len(self.points)-1):
                sameZ= newPoints[-1][1]==self.points[i][1] and newPoints[-1][1]==self.points[i+1][1]
                sameX= newPoints[-1][0]==self.points[i][0] and newPoints[-1][0]==self.points[i+1][0]
                xInbetween= isBetween(newPoints[-1][0],  self.points[i][0],  self.points[i+1][0])
                zInbetween= isBetween(newPoints[-1][1],  self.points[i][1],  self.points[i+1][1])
                if (sameZ and xInbetween) or (sameX and zInbetween):
                    continue
                newPoints.append(self.points[i])
            newPoints.append(self.points[-1])
            self.points=newPoints
            
            # TODO second pass: remove points that can be removed without changing the shape more than the tolerance
        def __repr__(self):
            return "<LineMove: feed={0}, p={1}>".format(str(self.feed), str(self.points))
            
            
    class BlockStart: # set RPM, tool, etc
        def  __init__(self, blockName, tool, rpm, feed):
            self.blockName=blockName
            self.tool=tool
            self.rpm=rpm
            self.feed=feed
        def __repr__(self):
            return "<BlockStart: {0}, ...>".format(self.blockName)
    
    
if __name__=="__main__":
    m=MachineCommand.LineMove([(1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (3, 6),  (3, 7), (4, 9)])
    print m
    m.simplify(tolerance=0)
    print m
