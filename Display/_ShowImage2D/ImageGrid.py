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
from .ImageTile import ImageTile
from .. import Common

class ImageGrid(QtWidgets.QFrame):
    """ Displays of grid of similarly sized images

    """
    signalScroll = QtCore.Signal(int)

    def __init__(self, controller, dataModel,
                 maxNumInRow):
        ''' Constructor

        Parameters
        ----------

        maxNumInRow : int
            max number of images in a row, before starting another row
        '''
        try:
            super(ImageGrid, self).__init__()


            self.controller = controller
            self.dataModel = dataModel
            
            self.currWidth = -1
            self.layout = QtWidgets.QGridLayout(self)
            self.layout.setSpacing(1)
            self.layout.setContentsMargins(0,0,0,0)

            self.numImages = dataModel.GetNumDatasets()
            self.numVisible = self.numImages

            if maxNumInRow is None:
                maxNumInRow = int(np.ceil(np.sqrt(self.numImages)))
            self.maxNumInRow = maxNumInRow
            


            self.imageFrameList = []
            self.visibleIndices = []

            xDescription = dataModel.commonState.dimsTable.iloc[0]
            yDescription = dataModel.commonState.dimsTable.iloc[1]
            currViewFn = dataModel.GetCurrViewValue
            self.visibleFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Visible')
            
            for imIndex in range(self.numImages):
                color = dataModel.GetDataTableValue(imIndex, 'Color')
                title = dataModel.GetDataTableValue(imIndex, 'Title')
                dataFn = lambda index=imIndex: dataModel.GetCurrDataSlice(index)
                imPanel = ImageTile(dim0Description=xDescription,
                                    dim1Description=yDescription,
                                    currViewFn=currViewFn,
                                    dataFn=dataFn,
                                    title = title,
                                    color=color)
                imPanel.signalScroll.connect(self.signalScroll)

                imPanel.signalChangeWindowLevel.connect(self.controller.signalChangeWindowLevel)
                imPanel.signalChangeLocation.connect(lambda xLoc, yLoc: self.controller.signalChangeDoubleDimLocation.emit(0, xLoc, 1, yLoc))
                self.imageFrameList.append(imPanel)
                rowIndex = imIndex // self.maxNumInRow
                colIndex = imIndex % self.maxNumInRow
                self.layout.addWidget(imPanel, rowIndex, colIndex)
                self.visibleIndices.append(imIndex)

            self.layout.setRowStretch(rowIndex+1, 10)

            
            self.currLocation = [self.dataModel.GetDimValue(0, 'CurrLocation'), self.dataModel.GetDimValue(1, 'CurrLocation')]

            self.controller.ViewChanged.connect(self.SyncDataAndView)
            self.controller.LocationChanged.connect(self.SyncLocation)
            self.controller.VisibleChanged.connect(self.SyncVisible)
            self.controller.WindowLevelChanged.connect(self.SyncWindowLevel)
            self.controller.NavModeChanged.connect(self.SyncNavMode)
            self.controller.signalChangeNumCols.connect(self.ChangeNumCols)
            
        except Exception as err:
            Common.HandleException(err)


    def SetSizes(self):
        self.SetWidth(self.currWidth)
    
    def SetWidth(self, width):
        self.currWidth = width
        numColumns = min(self.maxNumInRow, self.numVisible)
        if numColumns > 0:
            colWidth = int(width // numColumns) - 4 # 4 to account for border
            for imIndex in self.visibleIndices:
                frame = self.imageFrameList[imIndex]
                frame.SetWidth(colWidth)
              
            
    def ChangeNumCols(self, newNumCols):
        self.maxNumInRow = newNumCols
        self.SyncVisible()
        
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
                    
            #self.maxNumInRow = np.ceil(np.sqrt(numVisible))
            self.numVisible = numVisible
            self.SetSizes()            

            for visibleIndex in range(numVisible):
                imIndex = self.visibleIndices[visibleIndex]
                rowIndex = visibleIndex // self.maxNumInRow
                colIndex = visibleIndex % self.maxNumInRow
                currFrame = self.imageFrameList[imIndex]
                self.layout.addWidget(currFrame, rowIndex, colIndex)
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

        self.ShowIt()
        
    def SyncLocation(self):
        """ Updates location in all frames

        """
        try:
            self.currLocation = [self.dataModel.GetDimValue(0, 'CurrLocation'), self.dataModel.GetDimValue(1, 'CurrLocation')]
            for imIndex in self.visibleIndices:
                frame = self.imageFrameList[imIndex]
                frame.SyncLocation(self.currLocation)

            self.ShowIt()
        except Exception as err:
            Common.HandleException(err)

            
    def SyncWindowLevel(self):
        """ Updates window/level in all frames

        """
        window = self.dataModel.GetCurrViewValue('Window')
        level = self.dataModel.GetCurrViewValue('Level')
        
        for imIndex in self.visibleIndices:
            frame = self.imageFrameList[imIndex]
            frame.SyncWindowLevel(window, level)

        self.ShowIt()

    def sizeHint(self):
        return QtCore.QSize(900,800)
