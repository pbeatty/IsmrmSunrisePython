"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""

import numpy as np
from PyQt4 import QtGui, QtCore
import Display._Core as _Core
import Display._DisplayDefinitions as dd  

class _ControlWidget2D(QtGui.QWidget):
    from Display._DisplaySignals import *
    def __init__(self, complexImage=None, location=None, locationLabels=None, imageType=None, windowLevel=None, stats=None):
        _Core._create_qApp()        
        QtGui.QWidget.__init__(self)        

        controlLayout=QtGui.QGridLayout(self)
        layoutRowIndex = 0
        #
        # Image Type
        #        
        self.currImageType = dd.ImageType.mag
        
        self.imgTypeIndex = np.zeros(4, dtype=np.int)
        self.imgTypeIndex[dd.ImageType.mag] = 0        
        self.imgTypeIndex[dd.ImageType.phase] = 1
        self.imgTypeIndex[dd.ImageType.real] = 2
        self.imgTypeIndex[dd.ImageType.imag] = 3
        
        self.imageTypeLookup = np.zeros(4, dtype=np.int)
        self.imageTypeLookup[0] = dd.ImageType.mag        
        self.imageTypeLookup[1] = dd.ImageType.phase        
        self.imageTypeLookup[2] = dd.ImageType.real        
        self.imageTypeLookup[3] = dd.ImageType.imag        
        
        #imTypeLayout=QtGui.QHBoxLayout()
        label=QtGui.QLabel()
        label.setText("View")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        self.imgType=QtGui.QComboBox()
        self.imgType.addItem("Magnitude")
        self.imgType.addItem("Phase")
        self.imgType.addItem("Real")
        self.imgType.addItem("Imaginary")
        self.imgType.setCurrentIndex(self.imgTypeIndex[self.currImageType])
        QtCore.QObject.connect(self.imgType, QtCore.SIGNAL("currentIndexChanged(int)"), self.ImageTypeChanged)
#        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.imgType, layoutRowIndex, 1)        
        layoutRowIndex = layoutRowIndex + 1
        #
        # Window/Level
        #           
        self.currWindow=0.0
        self.currLevel=0.0
#        self.wlLayout=QtGui.QHBoxLayout()        
        self.window=QtGui.QDoubleSpinBox()                
        self.window.setDecimals(3)
        self.window.setMaximum(1.7*10**308)        
        self.window.setMaximumWidth (70) 
        self.level=QtGui.QDoubleSpinBox()                                
        self.level.setDecimals(3)
        self.level.setMaximum(1.7*10**308)
        self.level.setMinimum(-1.7*10**308)        
        self.level.setMaximumWidth (70) 
        label=QtGui.QLabel()
        label.setText("W")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)

        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)        
        controlLayout.addWidget(self.window, layoutRowIndex, 1)        
        layoutRowIndex = layoutRowIndex+1

        
        label=QtGui.QLabel()
        label.setText("L")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.level, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex+1
        
        button=QtGui.QPushButton("Default W/L")      
        controlLayout.addWidget(button, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex+1
        
        QtCore.QObject.connect(self.window, QtCore.SIGNAL("valueChanged(double)"), self.windowChanged)
        QtCore.QObject.connect(self.level, QtCore.SIGNAL("valueChanged(double)"), self.levelChanged)
        QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), self.windowLevelToDefaultPushed)
        
        #
        # Location    
        #
        self.location = location
#        locLayout=QtGui.QHBoxLayout()
        self.xcontrol=QtGui.QSpinBox()
        self.xcontrol.setMinimum(0)
        self.xcontrol.setMaximum(complexImage.shape[0]-1)
        self.xcontrol.setValue(location[0])
        self.ycontrol=QtGui.QSpinBox()
        self.ycontrol.setMinimum(0)
        self.ycontrol.setMaximum(complexImage.shape[1]-1)
        self.ycontrol.setValue(location[1])
                
                
        if locationLabels is None:
            locationLabels = ["X", "Y"]
        
        label=QtGui.QLabel()
        label.setText(locationLabels[0])
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)       
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.xcontrol, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1
        label=QtGui.QLabel()
        label.setText(locationLabels[1])
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.ycontrol, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1


        QtCore.QObject.connect(self.xcontrol, QtCore.SIGNAL("valueChanged(int)"), self.xLocationChanged)
        QtCore.QObject.connect(self.ycontrol, QtCore.SIGNAL("valueChanged(int)"), self.yLocationChanged)
       
        self.fnamePrefix = QtGui.QLineEdit()
        self.fnamePrefix.setText("hello")
        controlLayout.addWidget(self.fnamePrefix, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1
        
        saveButton=QtGui.QPushButton("Save")      
        controlLayout.addWidget(saveButton, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex+1
        QtCore.QObject.connect(saveButton, QtCore.SIGNAL("clicked()"), self.SavePushed)      
       
        statsLayout=QtGui.QGridLayout()
        if stats is not None:
            numImgs=len(stats)
            numStats=len(stats[0])            
            for imNum in range(numImgs):
                for stat in range(numStats):
                    label=QtGui.QLabel()
                    label.setText(str(stats[imNum][stat]))
                    statsLayout.addWidget(label,imNum,stat)
                
#        controlLayout.addLayout(imTypeLayout)
#        controlLayout.addLayout(locLayout)
#        controlLayout.addLayout(self.wlLayout)#this makes the controls widget the parent of all wlLayout's widgets
        #controlLayout.addLayout(statsLayout)
#        controlLayout.addStretch() 
        controlLayout.setRowStretch(layoutRowIndex, 10)        
#        self.controlLayout = controlLayout  

 #       print self.sizePolicy().horizontalPolicy()            
 #       self.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
 #       print self.sizePolicy().horizontalPolicy()        
        
    
    def xLocationChanged(self, x):
        if x != self.location[0]:
            self.location[0] = x
            self.signalLocationChange.emit(self.location[0], self.location[1])
        
    def yLocationChanged(self, y):
        if y != self.location[1]:
            self.location[1] = y
            self.signalLocationChange.emit(self.location[0], self.location[1])
        
        
    def ImageTypeChanged(self, index):        
        newImageType = self.imageTypeLookup[index]     
        if newImageType != self.currImageType:
            self.currImageType = newImageType
            self.signalImageTypeChange.emit(newImageType)

    def windowChanged(self, value):        
        if value != self.currWindow:
            self.currWindow = value            
            self.signalWindowLevelChange.emit(self.currWindow,self.currLevel)
    def levelChanged(self, value):        
        if value != self.currLevel:
            self.currLevel = value            
            self.signalWindowLevelChange.emit(self.currWindow,self.currLevel)
    def windowLevelToDefaultPushed(self):        
        self.signalWindowLevelReset.emit()

    def SavePushed(self):
        fnamePrefix = self.fnamePrefix.text()
        print fnamePrefix
        self.signalSaveToFile.emit(fnamePrefix)

    def SetImageType(self, newImageType):
        if newImageType != self.currImageType:
            self.currImageType = newImageType
            self.imgType.setCurrentIndex(self.imgTypeIndex[self.currImageType])                

    def ChangeLocation(self, x, y):
        self.location[0] = x
        self.location[1] = y
        self.xcontrol.setValue(x)
        self.ycontrol.setValue(y)
                    
    def ChangeWindowLevel(self, newIntensityWindow,newIntensityLevel):
        self.currWindow=newIntensityWindow
        self.currLevel=newIntensityLevel
        self.level.setValue(newIntensityLevel)
        self.window.setValue(newIntensityWindow)
        
    
        
        
