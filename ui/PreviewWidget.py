#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from MachineCommand import *

class PreviewWidget(QWidget):
    """
    Widget for viewing toolpaths and drawings
    """
    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)
        self.machineCodes=[]
        self.materialLength=0
        self.materialRadius=0
        self.previewStep=float("inf")
    
    def setMaterialSize(self, length, diameter):
        if self.materialLength == length and self.materialRadius == diameter/2:
            return
        self.materialLength=length
        self.materialRadius=diameter/2
        self.update()
    
    def showMachineCode(self, codeList):
        self.machineCodes=codeList
        self.update()
    
    def setPreviewStep(self, step):
        if self.previewStep==step:
            return
        self.previewStep=step
        self.update()
    
    def paintEvent(self, event):
        if self.width()==0 or self.height()==0:
            return
            
        painter=QPainter(self)
        black=QColor("black")
        thickPen=QPen(black)
        thickPen.setWidth(3)
        thickPen.setCosmetic(True)
        
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(10, self.height()/2)
        painter.scale(1, -1)
        painter.save()
        

        
        
        painter.restore()
        scaleFactor=max(self.materialLength/(self.width()-20), 2*self.materialRadius/(self.height()-20))
        if scaleFactor==0:
            return
        scaleFactor=1/scaleFactor
        painter.scale(scaleFactor, scaleFactor)
        materialRect=QRectF(0, 0, self.materialLength, self.materialRadius)
        painter.fillRect(materialRect, QColor("gray"))
        painter.setPen(QPen(QColor("white")))
        painter.drawRect(materialRect)
        
        painter.setPen(thickPen)
        path=QPainterPath()
        path.moveTo(0, self.height()/2)
        path.lineTo(0, 0)
        path.lineTo(self.width(),0)
        painter.drawPath(path)
        
        lastPoint=QPointF(999, 999) # TODO startpoint where?
        toolpathPen=QPen(QColor("blue"))
        toolpathPen.setWidthF(2.5)
        toolpathPen.setCosmetic(True)
        rapidMovePen=QPen(QColor("black"))
        rapidMovePen.setWidthF(1.5)
        rapidMovePen.setCosmetic(True)
        n=0
        for c in self.machineCodes:
            if n>self.previewStep:
                break
            n=n+1
            if isinstance(c, MachineCommand.LineMove):
                pa=QPainterPath()
                pa.moveTo(lastPoint)
                for p in c.points:
                    p=QPointF(p[1], p[0])
                    pa.lineTo(p)
                    lastPoint=p
                painter.setPen(toolpathPen)
                if c.feed==MachineCommand.RapidSpeed:
                    painter.setPen(rapidMovePen)
                painter.drawPath(pa)
            elif isinstance(c, MachineCommand.BlockStart):
                pass
            else:
                raise Exception("Unknown MachineCommand object for drawing: " + str(c))
        

        
        
