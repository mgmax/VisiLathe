#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt4.QtCore import *
from PyQt4.QtGui import *
import copy


class WorkerThread(QThread):
    # thanks to http://mrleeh.square7.ch/?cat=46 and the pyQt mandelbrot.py example
    workFinished = pyqtSignal()

    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.mutex=QMutex() # lock for accessing any data
        self.data=None
        self.output=None 
        self.doAbort=False
        self.doRestart=False
    
    def updateData(self, data):
        self.mutex.lock()
        self.data=copy.deepcopy(data)
        self.mutex.unlock()
    
    def restartWithData(self, data):
        self.updateData(data)
        self.restart()
    
    def abort(self):
        self.mutex.lock()
        if self.isRunning():
            self.doAbort=True
        self.mutex.unlock()
        
    def restart(self):
        # TODO rewrite... timing trouble!
        self.mutex.lock()
        if self.isRunning():
            self.doRestart=True
        else:
            self.start(QThread.LowPriority)
        self.mutex.unlock()
    
    def run(self):
        while True:
            self.mutex.lock()
            data=self.data
            self.mutex.unlock()
            
            output=None
            if not self.workShouldStop():
                output=self.doWork(data)
            
            tmp=copy.deepcopy(output)
            self.mutex.lock()
            self.output=tmp
            self.mutex.unlock()
            
            if self.doAbort:
                self.mutex.lock()
                self.doAbort=False
                self.mutex.unlock()
                return
            if self.doRestart:
                self.mutex.lock()
                self.doRestart=False
                self.mutex.unlock()
                continue
            self.workFinished.emit()
            break
    
    def doWork(self, data):
        for i in range(3):
            self.sleep(1000)
            if self.workShouldStop():
                return
        return 123
    
    def workShouldStop(self):
        return self.doAbort or self.doRestart
    
    def getOutput(self):
        print "Om"
        self.mutex.lock()
        output=self.output
        self.mutex.unlock()
        print "Oo"
        return output
    
class ToolpathThread(WorkerThread):
    def doWork(self, data):
        print "w"
        c=[]
        for t in data["toolpaths"]:
            c.extend(t.getMachineCode(data["globalSettings"]))
            if self.workShouldStop():
                print "wC"
                return
        print "wS"
        return c
