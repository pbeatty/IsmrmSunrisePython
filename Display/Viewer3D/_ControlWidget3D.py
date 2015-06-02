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
  

class _ControlWidget3D(QtGui.QWidget):
    from Display._DisplaySignals import *
    
    def __init__(self,image3DShape,initLocation, imageType, parent=None):        
        _Core._create_qApp()
        super(_ControlWidget3D,self).__init__()   
        self.image3DShape=image3DShape
        controlLayout=QtGui.QVBoxLayout(self)
        
        imTypeLayout=QtGui.QHBoxLayout()
        label=QtGui.QLabel()
        label.setText("Image Type")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        self.imgType=QtGui.QComboBox()
        #the order of these have to match DisplayDefinitions class...consider changing that class to a dictionary
        #to use here
        self.imgType.addItem("Real")
        self.imgType.addItem("Imaginary")
        self.imgType.addItem("Magnitude")
        self.imgType.addItem("Phase")        
        self.imgType.setCurrentIndex(imageType)        
        QtCore.QObject.connect(self.imgType, QtCore.SIGNAL("currentIndexChanged(int)"), self.changeImageType)
        imTypeLayout.addWidget(label)
        imTypeLayout.addWidget(self.imgType)        
        
        """
        cMapLayout=QtGui.QHBoxLayout()
        label=QtGui.QLabel()
        label.setText("Colormap")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        self.colorMap=QtGui.QComboBox()
        self.colorMap.addItem("Gray")
        self.colorMap.addItem("HSV")
        self.colorMap.setCurrentIndex(imageCMap)  
        QtCore.QObject.connect(self.colorMap, QtCore.SIGNAL("currentIndexChanged(int)"), self.changeCMap)
        cMapLayout.addWidget(label)
        cMapLayout.addWidget(self.colorMap)     
        """
        
        self.wlLayout=QtGui.QHBoxLayout()        
        self.window=QtGui.QDoubleSpinBox()        
        self.window.setMaximumWidth (70)               
        self.window.setDecimals(3)
        self.window.setMaximum(1.7*10**308)
        QtCore.QObject.connect(self.window, QtCore.SIGNAL("valueChanged(double)"), self.changeWindow)
        self.level=QtGui.QDoubleSpinBox() 
        self.level.setMaximumWidth (70)               
        self.level.setDecimals(3)
        self.level.setMaximum(1.7*10**308)
        self.level.setMinimum(-1.7*10**308)        
        self.level.setValue(np.floor(self.window.value()/2))
        QtCore.QObject.connect(self.level, QtCore.SIGNAL("valueChanged(double)"), self.changeLevel)
        label=QtGui.QLabel()
        label.setText("Window")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        self.wlLayout.addWidget(label)        
        self.wlLayout.addWidget(self.window)        
        label=QtGui.QLabel()
        label.setText("Level")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        self.wlLayout.addWidget(label)
        self.wlLayout.addWidget(self.level)
        button=QtGui.QPushButton("Default")
        QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), self.reset_wl)
        self.wlLayout.addWidget(button)
         
        locLayout=QtGui.QHBoxLayout()
        self.xcontrol=QtGui.QDoubleSpinBox()
        self.xcontrol.setDecimals(0)
        self.xcontrol.setMaximum(self.image3DShape[0]-1) 
        self.xcontrol.setValue(initLocation[0])
        QtCore.QObject.connect(self.xcontrol, QtCore.SIGNAL("valueChanged(double)"), self.changeXcontrol)
        self.ycontrol=QtGui.QDoubleSpinBox()
        self.ycontrol.setDecimals(0)
        self.ycontrol.setMaximum(self.image3DShape[1]-1)
        self.ycontrol.setValue(initLocation[1])
        QtCore.QObject.connect(self.ycontrol, QtCore.SIGNAL("valueChanged(double)"), self.changeYcontrol)
        self.zcontrol=QtGui.QDoubleSpinBox()
        self.zcontrol.setDecimals(0)
        self.zcontrol.setMaximum(self.image3DShape[2]-1)
        self.zcontrol.setValue(initLocation[2])
        QtCore.QObject.connect(self.zcontrol, QtCore.SIGNAL("valueChanged(double)"), self.changeZcontrol)
        
        
        label=QtGui.QLabel()
        label.setText("X")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)       
        locLayout.addWidget(label)
        locLayout.addWidget(self.xcontrol)
        label=QtGui.QLabel()
        label.setText("Y")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        locLayout.addWidget(label)
        locLayout.addWidget(self.ycontrol)
        label=QtGui.QLabel()
        label.setText("Z")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        locLayout.addWidget(label)
        locLayout.addWidget(self.zcontrol)
                
        controlLayout.addLayout(imTypeLayout)
        """controlLayout.addLayout(cMapLayout)"""
        controlLayout.addLayout(locLayout)
        controlLayout.addLayout(self.wlLayout)#this makes the controls widget the parent of all wlLayout's widgets
        controlLayout.addStretch() 
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
           
    
    #signals to emit when a control panel dial is changed    
    def changeImageType(self,index): 
        if self.imgType.hasFocus():
            self.signalImageTypeChange.emit(index) 
    """                       
    def changeCMap(self,index):
        if self.colorMap.hasFocus():
            self.signalImageCmapChanged.emit(index)      
    """
    def changeWindow(self,value):   
        if self.window.hasFocus():
            self.signalWindowLevelChange.emit(value,self.level.value())            
    def changeLevel(self,value):
        if self.level.hasFocus():
            self.signalWindowLevelChange.emit(self.window.value(),value) 
    def changeXcontrol(self,value): 
        if self.xcontrol.hasFocus():
            self.signalXLocationChange.emit(value)            
    def changeYcontrol(self,value):
        if self.ycontrol.hasFocus():
            self.signalYLocationChange.emit(value)            
    def changeZcontrol(self,value):
        if self.zcontrol.hasFocus():
            self.signalZLocationChange.emit(value)            
    def reset_wl(self):
        self.signalWindowLevelReset.emit()

    #slots to update control dials when settings are changed 
    #using mechanisms other than the control panel
    def onXChange(self,value):        
        self.xcontrol.setValue(value)
    def onYChange(self,value):
        self.ycontrol.setValue(value)
    def onZChange(self,value):
        self.zcontrol.setValue(value)
    def onImageTypeChange(self,index):
        self.imgType.setCurrentIndex(index)
    def onImageCMapChange(self,index):
        self.colorMap.setCurrentIndex(index)
    def onWindowLevelChange(self,windowValue,levelValue):
        self.window.setValue(windowValue)
        self.level.setValue(levelValue)
    def onWindowLevelReset(self):
        self.window.setValue(0.0)
        self.level.setValue(0.0)
        
            