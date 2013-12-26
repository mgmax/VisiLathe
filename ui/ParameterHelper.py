#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import *

class ParameterHelper:
    """Helper Class for synchronising values between dictionary-keys and GUI objects
    params: list of dicts: [{"name":"key name", "object":Qt-gui-object, "default":default_value, "type":(currently unused)}, {...}, ... ]
    values: dict: {"key name 1":1234, "whatever":345, ...}
    """
    @staticmethod
    def getValuesFromGUI(params):
        values={}
        for p in params:
            obj=p["object"]
            if isinstance(obj, QtGui.QAbstractSpinBox):
                val=obj.value()
            elif isinstance(obj, QtGui.QComboBox):
                val=obj.currentIndex()
            elif isinstance(obj, QtGui.QLineEdit):
                val=obj.text()
            else:
                raise Exception("cannot get parameter value from unknown GUI object "+str(obj))
            values[p["name"]]=val
        return values
    
    @staticmethod
    def setValuesInGUI(params, values):
        for p in params:
            obj=p["object"]
            val=values[p["name"]]
            if isinstance(obj, QtGui.QAbstractSpinBox):
                obj.setValue(val)
            elif isinstance(obj, QtGui.QComboBox):
                obj.setCurrentIndex(val)
            elif isinstance(obj, QtGui.QLineEdit):
                obj.setText(val)
            else:
                raise Exception("cannot set parameter value for unknown GUI object "+str(obj))
            values[p["name"]]=val
        return values
