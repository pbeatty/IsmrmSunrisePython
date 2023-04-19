"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Alan Kuurstra
Philip J. Beatty (philip.beatty@gmail.com)

2017, modified by Chad Harris
2017, modified by Philip Beatty
"""

from qtpy import QtWidgets, QtCore
import numpy as np
from IPython.display import display

from .ImageTile import ImageTile
from .. import Common

class ImageMosaic(QtWidgets.QFrame):
    """ Displays similarly sized images

    """
    signalChangeLocation = QtCore.Signal(int, int)
    signalChangeWindowLevel = QtCore.Signal(float, float)
    signalScroll = QtCore.Signal(int)
    signalResizeColumns = QtCore.Signal()
    
    def __init__(self,
                 dim0Description,
                 dim1Description,
                 currViewFn,
                 dataFn,
                 visibleFn,
                 title,
                 numImages,
                 maxNumInRow):
        ''' Constructor

        Parameters
        ----------

        currView : pandas Series containing
            Window, Level, EnableWindowLevelChange, Colormap, Interpolation, Origin

        imageDataFn : lambda
            Given image index, returns float image (all images same size)

        maxNumInRow : int
            max number of images in a row, before starting another row
        '''
        try:

            super(ImageMosaic, self).__init__()

            self.currLocation = [dim0Description.get('CurrLocation'), dim1Description.get('CurrLocation')]
            self.aspectRatio = dim1Description.get('Shape') * (1.0/dim0Description.get('Shape'))

            self.title = title
            self.setStyleSheet("* {padding: 0; margin: 0; border: 0;}")

            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(3)
            self.numImages = numImages
            if maxNumInRow is None:
                maxNumInRow = np.ceil(np.sqrt(self.numImages))
            self.maxNumInRow = maxNumInRow


            self.imageFrameList = []
            self.visibleIndices = []

            rowOffset = 0
            
            if title is not None:
                self.titleLabel = QtWidgets.QLabel()
                self.titleLabel.setText(title)
                self.titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.titleLabel.setMinimumHeight(20)
                self.titleLabel.setMaximumHeight(20)
                self.layout.addWidget(self.titleLabel)

                rowOffset = 1

            self.visibleFn = visibleFn
            
            for imIndex in range(self.numImages):

                imPanel = ImageTile(dim0Description,
                                    dim1Description,
                                    currViewFn,
                                    lambda index=imIndex: dataFn(index));
                
                
                imPanel.setMinimumHeight(10)
                imPanel.signalChangeWindowLevel.connect(self.signalChangeWindowLevel)
                imPanel.signalChangeLocation.connect(self.signalChangeLocation)
                imPanel.signalScroll.connect(self.signalScroll)
                self.imageFrameList.append(imPanel)
                self.layout.addWidget(imPanel)
                self.visibleIndices.append(imIndex)

            self.layout.addStretch(100)
                
        except Exception as err:
            Common.HandleException(err)



    def resizeEvent(self, e):
        self.signalResizeColumns.emit()
        
    def GetMinRowHeight(self):
        return self.aspectRatio * self.width()

    def SetRowHeight(self, height):
        for imIndex in self.visibleIndices:
            frame = self.imageFrameList[imIndex]
            frame.setMinimumHeight(height)
            frame.setMaximumHeight(height)
            frame.resize(frame.width(), height)
            
            
    def SyncVisible(self):
        """ synchronizes which plots are displayed with visibleFn

        visibleFn : lambda, takes image index and returns True/False
        """
        try:
            for imIndex in reversed(self.visibleIndices):
                self.layout.removeWidget(self.imageFrameList[imIndex])
                self.imageFrameList[imIndex].hide()
            
            numVisible = 0
            self.visibleIndices = []
            for imIndex in range(self.numImages):
                if self.visibleFn(imIndex):
                    numVisible += 1
                    self.visibleIndices.append(imIndex)
                    

            for visibleIndex in range(numVisible):
                imIndex = self.visibleIndices[visibleIndex]
                currFrame = self.imageFrameList[imIndex]
                self.layout.addWidget(currFrame)
                currFrame.show()
                currFrame.SyncLocation(self.currLocation)
                currFrame.SyncDataAndView()
                currFrame.ShowIt()
                                       

        except Exception as err:
            Common.HandleException(err)


    def SyncNavMode(self, mode):
        '''

        Parameters
        ----------

        mode : 'ZOOM', 'PAN' or None
        '''
        self.navMode = mode
        for imIndex in self.visibleIndices:
            frame = self.imageFrameList[imIndex]
            frame.SyncNavMode(mode)


    def ShowIt(self):
        """ refresh display

        """
        for imIndex in self.visibleIndices:
            frame = self.imageFrameList[imIndex]
            frame.ShowIt()
            
    def SyncDataAndView(self):
        """ Updates all frames with new data and view info

        """
        for imIndex in self.visibleIndices:
            frame = self.imageFrameList[imIndex]
            frame.SyncDataAndView()


    def SyncLocation(self, currLocation):
        """ Updates location in all frames

        """
        try:
            self.currLocation=currLocation
            for imIndex in self.visibleIndices:
                frame = self.imageFrameList[imIndex]
                frame.SyncLocation(currLocation)
        except Exception as err:
            Common.HandleException(err)

    def SyncWindowLevel(self, window, level):
        """ Updates window/level in all frames

        """
        
        for imIndex in self.visibleIndices:
            frame = self.imageFrameList[imIndex]
            frame.SyncWindowLevel(window, level)
