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

from .ImageMosaic import ImageMosaic
from .ColumnKey import ColumnKey
from .. import Common

from datetime import datetime

class FixedWidthBottomStretchContainer(QtWidgets.QFrame):
    def __init__(self, contents, width):
        try:
            super(FixedWidthBottomStretchContainer, self).__init__()

            self.setObjectName("FWBSC")
            self.setStyleSheet("#FWBSC {{background-color: {};}}".format(Common.darkBackgroundColor))
            self.setMinimumWidth(width)
            self.setMaximumWidth(width)
            
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)            
            self.layout.addWidget(contents)
            self.layout.addStretch(10)
        except Exception as err:
            Common.HandleException(err)


class BottomStretchContainer(QtWidgets.QFrame):
    def __init__(self, contents):
        try:
            super(BottomStretchContainer, self).__init__()
            
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)            
            self.layout.addWidget(contents)
            self.layout.addStretch(10)
        except Exception as err:
            Common.HandleException(err)


            

class OrthoImageMosaic(QtWidgets.QFrame):
    """ Displays columns of orthogonal images

    """
    signalScroll = QtCore.Signal(int)
    def __init__(self, controller, dataModel):
        ''' Constructor

        Parameters
        ----------

        dimsTable : pandas DataFrame
          Row for each dimension, containing Name, Shape, CurrLocation, Color

        currView : pandas Series containing
            Window, Level, EnableWindowLevelChange, Colormap, Interpolation, Origin

        imageDataFn : lambda
            Given image index, returns float image (all images same size)

        imageDescription : pandas DataFrame containing Title, Color, Index for all images

        maxNumInRow : int
            max number of images in a row, before starting another row
        '''
        try:
            super(OrthoImageMosaic, self).__init__()
            self.controller = controller
            self.dataModel = dataModel
            self.window = self.dataModel.GetCurrViewValue('Window')
            self.level = self.dataModel.GetCurrViewValue('Level')

            self.controller.ViewChanged.connect(self.SyncDataAndView)
            self.controller.LocationChanged.connect(self.SyncLocation)
            self.controller.VisibleChanged.connect(self.SyncVisible)
            self.controller.WindowLevelChanged.connect(self.SyncWindowLevel)
            self.controller.NavModeChanged.connect(self.SyncNavMode)
            
            self.currRowHeight = -1
            self.setObjectName("OrthoImageMosaic")
            self.setStyleSheet("* {padding: 0; margin: 0; border: 0;}")


            self.currLocation = dataModel.commonState.dimsTable['CurrLocation'].copy()

            self.numImages = dataModel.GetNumDatasets()

            xDescription = dataModel.commonState.dimsTable.iloc[0]
            yDescription = dataModel.commonState.dimsTable.iloc[1]
            zDescription = dataModel.commonState.dimsTable.iloc[2]
            currViewFn = dataModel.GetCurrViewValue
            visibleFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Visible')

            self.XYColumn = ImageMosaic(xDescription,
                                        yDescription,
                                        currViewFn,
                                        dataModel.GetCurrXYPlane,
                                        visibleFn,
                                        "XY",
                                        self.numImages,
                                        1)
            #print("{}: XYColumn created".format(datetime.now().strftime('%X.%f')))

            self.YZColumn = ImageMosaic(yDescription,
                                        zDescription,
                                        currViewFn,
                                        dataModel.GetCurrYZPlane,
                                        visibleFn,
                                        "YZ",
                                        self.numImages,
                                        1)
            #print("{}: YZColumn created".format(datetime.now().strftime('%X.%f')))

            self.ZXColumn = ImageMosaic(zDescription,
                                        xDescription,
                                        currViewFn,
                                        dataModel.GetCurrZXPlane,
                                        visibleFn,
                                        "ZX",
                                        self.numImages,
                                        1)
            #print("{}: ZXColumn created".format(datetime.now().strftime('%X.%f')))

            
            
            
            self.layout = QtWidgets.QHBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)
            self.splitter = QtWidgets.QSplitter()
            self.splitter.addWidget(BottomStretchContainer(self.XYColumn))
            self.splitter.addWidget(BottomStretchContainer(self.YZColumn))
            self.splitter.addWidget(BottomStretchContainer(self.ZXColumn))
                        

            keyWidth=4
            self.key = ColumnKey("", dataModel, keyWidth)
            self.layout.addWidget(FixedWidthBottomStretchContainer(self.key, keyWidth))
            self.layout.addWidget(self.splitter)
                
                
            self.XYColumn.signalChangeWindowLevel.connect(self.controller.signalChangeWindowLevel)
            self.YZColumn.signalChangeWindowLevel.connect(self.controller.signalChangeWindowLevel)
            self.ZXColumn.signalChangeWindowLevel.connect(self.controller.signalChangeWindowLevel)

            self.XYColumn.signalScroll.connect(self.signalScroll)
            self.YZColumn.signalScroll.connect(self.signalScroll)
            self.ZXColumn.signalScroll.connect(self.signalScroll)
            
            self.XYColumn.signalChangeLocation.connect(lambda xLoc, yLoc: self.controller.signalChangeDoubleDimLocation.emit(0, xLoc, 1, yLoc))
            self.YZColumn.signalChangeLocation.connect(lambda yLoc, zLoc: self.controller.signalChangeDoubleDimLocation.emit(1, yLoc, 2, zLoc))
            self.ZXColumn.signalChangeLocation.connect(lambda zLoc, xLoc: self.controller.signalChangeDoubleDimLocation.emit(0, xLoc, 2, zLoc))

            self.XYColumn.signalResizeColumns.connect(self.ResizeColumns)
            self.YZColumn.signalResizeColumns.connect(self.ResizeColumns)
            self.ZXColumn.signalResizeColumns.connect(self.ResizeColumns)


            
            
        except Exception as err:
            Common.HandleException(err)




    def resizeEvent(self, e):
        self.ResizeColumns()
        
    def ResizeColumns(self):
        minXYRowHeight = self.XYColumn.GetMinRowHeight()
        minYZRowHeight = self.YZColumn.GetMinRowHeight()
        minZXRowHeight = self.ZXColumn.GetMinRowHeight()

        newRowHeight = round(max(minXYRowHeight, minYZRowHeight, minZXRowHeight))

        if newRowHeight != self.currRowHeight:
            self.currRowHeight = newRowHeight
            self.key.SetRowHeight(self.currRowHeight)
            self.XYColumn.SetRowHeight(self.currRowHeight)
            self.YZColumn.SetRowHeight(self.currRowHeight)
            self.ZXColumn.SetRowHeight(self.currRowHeight)
            
    def SyncVisible(self):
        """ synchronizes which plots are displayed with visibleFn

        visibleFn : lambda, takes image index and returns True/False
        """
        try:
            self.key.SyncVisible()
            self.XYColumn.SyncVisible()
            self.YZColumn.SyncVisible()
            self.ZXColumn.SyncVisible()
            
        except Exception as err:
            Common.HandleException(err)


    def SyncNavMode(self, mode):
        '''

        Parameters
        ----------

        mode : 'ZOOM', 'PAN' or None
        '''
        self.XYColumn.SyncNavMode(mode)
        self.YZColumn.SyncNavMode(mode)
        self.ZXColumn.SyncNavMode(mode)
        

    def SyncDataAndView(self):
        """ Updates all frames with new data and view info

        """
        self.window = self.dataModel.GetCurrViewValue('Window')
        self.level = self.dataModel.GetCurrViewValue('Level')

        self.XYColumn.SyncDataAndView()
        self.YZColumn.SyncDataAndView()
        self.ZXColumn.SyncDataAndView()
        self.XYColumn.ShowIt()
        self.YZColumn.ShowIt()
        self.ZXColumn.ShowIt()

        
    def SyncLocation(self):
        try:
            
            newX = self.dataModel.GetDimValue(0, 'CurrLocation')
            newY = self.dataModel.GetDimValue(1, 'CurrLocation')
            newZ = self.dataModel.GetDimValue(2, 'CurrLocation')

            xChange = newX != self.currLocation[0]
            yChange = newY != self.currLocation[1]
            zChange = newZ != self.currLocation[2]

            if( xChange or yChange or zChange):
                
                self.currLocation = [newX, newY, newZ]
            
                if( zChange ):
                    self.XYColumn.SyncDataAndView()
                if( xChange):
                    self.YZColumn.SyncDataAndView()
                if( yChange):
                    self.ZXColumn.SyncDataAndView()

                if( xChange or yChange):
                    self.XYColumn.SyncLocation([newX, newY])
                if( yChange or zChange):
                    self.YZColumn.SyncLocation([newY, newZ])
                if( zChange or xChange):
                    self.ZXColumn.SyncLocation([newZ, newX])

                self.XYColumn.ShowIt()
                self.YZColumn.ShowIt()
                self.ZXColumn.ShowIt()
                                
                    
                
        except Exception as err:
            Common.HandleException(err)

    def SyncWindowLevel(self):
        """ Updates window/level in all frames

        """
        if(self.dataModel.GetCurrViewValue('EnableWindowLevelChange')):
            newWindow = self.dataModel.GetCurrViewValue('Window')
            newLevel = self.dataModel.GetCurrViewValue('Level')

            if(newWindow != self.window or newLevel != self.level):
                self.window = newWindow
                self.level = newLevel
                self.XYColumn.SyncWindowLevel(self.window, self.level)
                self.YZColumn.SyncWindowLevel(self.window, self.level)
                self.ZXColumn.SyncWindowLevel(self.window, self.level)
        

