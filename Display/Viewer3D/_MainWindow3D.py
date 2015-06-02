"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""

from PyQt4 import QtGui, QtCore
import Display._Core as _Core
import Display._DisplayDefinitions as dd       
import _MplImage3D
import _ControlWidget3D


class _MainWindow(QtGui.QMainWindow):
    def __init__(self,complexIm3,interpolation='bicubic', initLocation=None, imageType=dd.ImageType.mag):
        _Core._create_qApp()         
        super(_MainWindow,self).__init__()    
        if initLocation is None:            
            initLocation=[complexIm3.shape[0]/2,complexIm3.shape[1]/2,complexIm3.shape[2]/2]
        
        self.setWindowTitle('3D Viewer')  
        self.viewerNumber=0
        self.imagePanel3D=_MplImage3D._MplImage3D(complexIm3,interpolation,initLocation,imageType,parent=self)
        self.controls=_ControlWidget3D._ControlWidget3D(complexIm3.shape,initLocation,imageType,parent=self)               
        
        mprWidget=QtGui.QWidget()             
        layoutmpr = QtGui.QGridLayout()         
        layoutmpr.addWidget(self.controls,1,0)
        layoutmpr.addWidget(self.imagePanel3D.xsliceNav,2,0)        
        layoutmpr.addWidget(self.imagePanel3D.xslice,3,0)        
        layoutmpr.addWidget(self.imagePanel3D.ysliceNav,0,1)         
        layoutmpr.addWidget(self.imagePanel3D.yslice,1,1)        
        layoutmpr.addWidget(self.imagePanel3D.zsliceNav,2,1)        
        layoutmpr.addWidget(self.imagePanel3D.zslice,3,1)
        mprWidget.setLayout(layoutmpr)
        
        plotsWidget=QtGui.QWidget()
        layoutplots=QtGui.QVBoxLayout()
        layoutplots.addWidget(self.imagePanel3D.xplot)        
        layoutplots.addWidget(self.imagePanel3D.yplot)        
        layoutplots.addWidget(self.imagePanel3D.zplot)  
        plotsWidget.setLayout(layoutplots)
        
        splitter=QtGui.QSplitter()
        splitter.addWidget(mprWidget)
        splitter.addWidget(plotsWidget)
        
        #mainLayout = QtGui.QHBoxLayout()
        #mainLayout.addWidget(splitter)
        #self.setLayout(mainLayout) #used when inheriting from QDialog
        
        self.setCentralWidget(splitter) #used when inheriting from QMainWindow
        #self.statusBar().showMessage('Ready') 
        
        self.makeConnections()
        
        self.show()
        self.setFocus()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def makeConnections(self):
        self.controls.signalImageTypeChange.connect(self.imagePanel3D.onImageTypeChange)
        """self.controls.signalImageCmapChanged.connect(self.imagePanel3D.CMapChanged)"""
        
        #when cursor moves, update lines
        self.imagePanel3D.zslice.signalXLocationChange.connect(self.imagePanel3D.onXChange)
        self.imagePanel3D.zslice.signalYLocationChange.connect(self.imagePanel3D.onYChange)
        self.imagePanel3D.zslice.signalZLocationChange.connect(self.imagePanel3D.onZChange)
        
        self.imagePanel3D.xslice.signalXLocationChange.connect(self.imagePanel3D.onXChange)
        self.imagePanel3D.xslice.signalYLocationChange.connect(self.imagePanel3D.onYChange)
        self.imagePanel3D.xslice.signalZLocationChange.connect(self.imagePanel3D.onZChange)
        
        self.imagePanel3D.yslice.signalXLocationChange.connect(self.imagePanel3D.onXChange)
        self.imagePanel3D.yslice.signalYLocationChange.connect(self.imagePanel3D.onYChange)
        self.imagePanel3D.yslice.signalZLocationChange.connect(self.imagePanel3D.onZChange)
        
        #when cursor moves, update controls
        self.imagePanel3D.xslice.signalXLocationChange.connect(self.controls.onXChange)
        self.imagePanel3D.xslice.signalYLocationChange.connect(self.controls.onYChange)
        self.imagePanel3D.xslice.signalZLocationChange.connect(self.controls.onZChange)
        
        self.imagePanel3D.yslice.signalXLocationChange.connect(self.controls.onXChange)
        self.imagePanel3D.yslice.signalYLocationChange.connect(self.controls.onYChange)
        self.imagePanel3D.yslice.signalZLocationChange.connect(self.controls.onZChange)
        
        self.imagePanel3D.zslice.signalXLocationChange.connect(self.controls.onXChange)
        self.imagePanel3D.zslice.signalYLocationChange.connect(self.controls.onYChange)
        self.imagePanel3D.zslice.signalZLocationChange.connect(self.controls.onZChange)
        
        #when right button pressed, update window/level of images
        self.imagePanel3D.xslice.signalWindowLevelChange.connect(self.imagePanel3D.onWindowLevelChange)
        self.imagePanel3D.yslice.signalWindowLevelChange.connect(self.imagePanel3D.onWindowLevelChange)
        self.imagePanel3D.zslice.signalWindowLevelChange.connect(self.imagePanel3D.onWindowLevelChange)
        
        #when right button pressed, update window/level controls
        self.imagePanel3D.xslice.signalWindowLevelChange.connect(self.controls.onWindowLevelChange)
        self.imagePanel3D.yslice.signalWindowLevelChange.connect(self.controls.onWindowLevelChange)
        self.imagePanel3D.zslice.signalWindowLevelChange.connect(self.controls.onWindowLevelChange)
        
        
        #when location control changes, update lines
        self.controls.signalXLocationChange.connect(self.imagePanel3D.onXChange)
        self.controls.signalYLocationChange.connect(self.imagePanel3D.onYChange)
        self.controls.signalZLocationChange.connect(self.imagePanel3D.onZChange)
        
        #when window/level control changes, update images
        self.controls.signalWindowLevelChange.connect(self.imagePanel3D.onWindowLevelChange)
        
        #when window/level reset pressed, update images and control
        self.controls.signalWindowLevelReset.connect(self.controls.onWindowLevelReset)
        self.controls.signalWindowLevelReset.connect(self.imagePanel3D.onWindowLevelReset)
                
    
    def keyPressEvent(self,event):
        #print event.text() #this one can tell when shift is being held down
        key=event.key()
        if key==77:
            self.imagePanel3D.onImageTypeChange(dd.ImageType.mag)
            self.controls.onImageTypeChange(dd.ImageType.mag)
        elif key==80:
            self.imagePanel3D.onImageTypeChange(dd.ImageType.phase)
            self.controls.onImageTypeChange(dd.ImageType.phase)
        elif key==82:
            self.imagePanel3D.onImageTypeChange(dd.ImageType.real)
            self.controls.onImageTypeChange(dd.ImageType.real)
        elif key==73:
            self.imagePanel3D.onImageTypeChange(dd.ImageType.imag) 
            self.controls.onImageTypeChange(dd.ImageType.imag)
        event.ignore()
    
    def setViewerNumber(self,number):
        self.viewerNumber=number
        
    def closeEvent(self,event):   
        if self.viewerNumber:
            del  _Core._viewerList[self.viewerNumber]
        
  
        

       