"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""
import numpy as np
from PyQt4 import QtCore,QtGui
import Display._Core as _Core
from Display._NavigatorToolbar import NavigationToolbar
import Display._MplImage as _MplImage
import Display._MplPlot as _MplPlot
import Display._DisplayDefinitions as dd  
import _ControlWidget2D

class _MainWindow(QtGui.QMainWindow): 
    def __init__(self,complexIm,interpolation='bicubic', origin='lower', titles=None, locationLabels=None, maxNumInRow=None, colormap=None):
        _Core._create_qApp()  
        super(_MainWindow,self).__init__() 
        self.setWindowTitle('Plot')      
        self.viewerNumber=0
        self.complexIm = np.copy(complexIm)   
        if self.complexIm.ndim == 2:
            self.complexIm = self.complexIm[:,:,np.newaxis]  
        numImages = self.complexIm.shape[2]
        initLocation=[int(complexIm.shape[0]/2),int(complexIm.shape[1]/2)]        
        imageType=dd.ImageType.mag
        
        #
        # give each image a label
        #
        if type(titles) is list and len(titles)==1:
            titles=titles[0]
        elif type(titles) is list and len(titles)!=numImages:
            titles=None        
        if numImages==1 and titles is None:
            titles=[""]
        elif numImages==1 and type(titles) is str:
            titles=[titles]
        elif numImages>1 and type(titles) is str:
            prefix=titles
            titles=[]
            for imIndex in range(numImages):
                titles.append(prefix+str(imIndex))
        elif numImages>1 and type(titles) is list:
            pass
        else:
            titles=[]
            for imIndex in range(numImages):
                titles.append("Image "+str(imIndex)) 
        self.titles = titles
        #
        # Set up Controls
        #
        stats=[["Image","Min","Max","Mean","Std"]]
        for imNum in range(numImages):
            stats.append(\
            [titles[imNum],\
            self.complexIm[:,:,imNum].min(),\
            self.complexIm[:,:,imNum].max(),\
            self.complexIm[:,:,imNum].mean(),\
            self.complexIm[:,:,imNum].std()])
        self.controls = _ControlWidget2D._ControlWidget2D(complexImage=complexIm, location=initLocation, imageType=imageType,stats=stats, locationLabels=locationLabels) 
        
        #
        # Set up image panels
        #   
        self.imagePanels=QtGui.QWidget(self)
        colors=dd.PlotColours.colours
        
        
        self.imagePanelsList = []
        self.imagePanelToolbarsList=[]
        if locationLabels is None:
            locationLabels = ["X", "Y"]
        for imIndex in range(numImages):
            labels= [{'color': 'r', 'textLabel': locationLabels[0]},{'color': 'b', 'textLabel': locationLabels[1]},{'color': colors[imIndex], 'textLabel': titles[imIndex]}]            
            self.imagePanelsList.append(_MplImage._MplImage(complexImage=self.complexIm[:,:,imIndex], interpolation=interpolation, origin=origin, location=initLocation, imageType=imageType, locationLabels=labels, colormap=colormap))                
            self.imagePanelToolbarsList.append(NavigationToolbar(self.imagePanelsList[imIndex],self.imagePanelsList[imIndex]))
        """
        # Synchronize the starting window/leveling to agree with the first panel        
        for imIndex in range(1,numImages):            
            self.imagePanelsList[imIndex].intensityLevelCache=self.imagePanelsList[0].intensityLevelCache
            self.imagePanelsList[imIndex].intensityWindowCache=self.imagePanelsList[0].intensityWindowCache
        self.ChangeWindowLevel(self.imagePanelsList[0].intensityWindowCache[imageType],self.imagePanelsList[0].intensityLevelCache[imageType])
        """
        imLayout = QtGui.QGridLayout()
        if maxNumInRow is None:
            maxNumInRow=int(np.sqrt(numImages)+1-1e-10)
        for imIndex in range(numImages):            
            imLayout.addWidget(self.imagePanelToolbarsList[imIndex],2*np.floor(imIndex/maxNumInRow),imIndex%maxNumInRow)
            imLayout.addWidget(self.imagePanelsList[imIndex],2*np.floor(imIndex/maxNumInRow)+1,imIndex%maxNumInRow)
        self.imagePanels.setLayout(imLayout)
        
        #
        # Set up plots
        #
        self.plotsPanel=QtGui.QWidget(self)           
        self.xPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[:,initLocation[1],:], title=locationLabels[0], dataType=imageType,colors=colors,initMarkerPosn=initLocation[1])
        self.yPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[initLocation[0],:,:], title=locationLabels[1], dataType=imageType,colors=colors,initMarkerPosn=initLocation[0])
        plotsLayout=QtGui.QVBoxLayout()        
        plotsLayout.addWidget(self.xPlotPanel)        
        plotsLayout.addWidget(self.yPlotPanel)
        self.plotsPanel.setLayout(plotsLayout)
        
        #make each section resizeable using a splitter                     
        splitter=QtGui.QSplitter(QtCore.Qt.Horizontal)        
        splitter.addWidget(self.controls)
        splitter.addWidget(self.imagePanels)
        splitter.addWidget(self.plotsPanel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        
        
        #self.mainLayout = QtGui.QHBoxLayout()
        #self.mainLayout.addWidget(splitter)        
        #self.setLayout(self.mainLayout) #used when inheriting from QDialog
        
        self.setCentralWidget(splitter) #used when inheriting from QMainWindow
        #self.statusBar().showMessage('Ready')         
        
        self.makeConnections() 

        self.show()
        self.setFocus()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
               
    def makeConnections(self):        
        # Connect from controls        
        self.controls.signalImageTypeChange.connect(self.ChangeImageType)                        
        self.controls.signalLocationChange.connect(self.ChangeLocation)        
        self.controls.signalWindowLevelChange.connect(self.ChangeWindowLevel)
        self.controls.signalWindowLevelReset.connect(self.SetWindowLevelToDefault)
        self.controls.signalSaveToFile.connect(self.SaveToFile)         
         
        # Connect from imagePanel       
        for currImagePanel in self.imagePanelsList:
            currImagePanel.signalLocationChange.connect(self.ChangeLocation)
            currImagePanel.signalWindowLevelChange.connect(self.ChangeWindowLevel)        
        
    def ChangeImageType(self, imageType):
        self.controls.SetImageType(imageType)
        self.xPlotPanel.showDataTypeChange(imageType)
        self.yPlotPanel.showDataTypeChange(imageType)        

        for currImagePanel in self.imagePanelsList:
            currImagePanel.showImageTypeChange(imageType)
        
    def SaveToFile(self, fnamePrefix):
        for panelIndex in range(len(self.imagePanelsList)):
            currImagePanel = self.imagePanelsList[panelIndex]
            currFname = "{prefix}-{index:0>2d}-{desc}".format(prefix=fnamePrefix, index=panelIndex, desc=self.titles[panelIndex])
            print currFname
            currImagePanel.SaveImage(currFname)            
    def ChangeWindowLevel(self, newIntensityWindow,newIntensityLevel):
        self.controls.ChangeWindowLevel(newIntensityWindow,newIntensityLevel)
        numImages = len(self.imagePanelsList)
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showWindowLevelChange(newIntensityWindow,newIntensityLevel)
            
    def SetWindowLevelToDefault(self):
        self.controls.ChangeWindowLevel(0,0)
        
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showSetWindowLevelToDefault()
        
    def ChangeLocation(self, x, y):      
        self.controls.ChangeLocation(x, y)
        self.xPlotPanel.showComplexDataAndMarkersChange(self.complexIm[:,y,:],x)
        self.yPlotPanel.showComplexDataAndMarkersChange(self.complexIm[x,:,:],y)
        numImages = len(self.imagePanelsList)
        for imIndex in range(numImages):
            self.imagePanelsList[imIndex].showLocationChange([x,y])

    def keyPressEvent(self,event):
        #print event.text() #this one can tell when shift is being held down
        key=event.key()
        if key==77:
            self.ChangeImageType(dd.ImageType.mag)
        elif key==80:
            self.ChangeImageType(dd.ImageType.phase)
        elif key==82:
            self.ChangeImageType(dd.ImageType.real)
        elif key==73:
            self.ChangeImageType(dd.ImageType.imag)     
        event.ignore()
    
    def setViewerNumber(self,number):
        self.viewerNumber=number
        
    def closeEvent(self,event):   
        if self.viewerNumber:
            del  _Core._viewerList[self.viewerNumber]

        
        

  
        
        
        