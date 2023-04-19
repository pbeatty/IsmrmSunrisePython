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
__all__ = ["CrossSections"]

from qtpy import QtWidgets, QtCore
import numpy as np
from ..ImagePanelObjects import PlotPanel as PlotPanel
from .. import Common

from IPython.display import display


def ComputeYLimits(dataModel):
    dataMin = dataModel.GetCurrViewValue('DataMin')
    dataMax = dataModel.GetCurrViewValue('DataMax')
    dataRange = dataMax-dataMin
    margin = dataRange * 0.05 + 0.001
    return [dataMin-margin, dataMax+margin]


class CrossSections(QtWidgets.QFrame):
    #    signalChangeSingleDimLocation = QtCore.Signal(int, int)
    def __init__(self,
                 controller,
                 dataModel):
        '''
         Construct CrossSections

        Parameters
        ----------

        controller : requires VisibleChanged, LocationChanged, ViewChanged, NavModeChanged, signalChangeSingleDimLocation

        dataModel : pandas based data model

        '''
        try:
            super(CrossSections, self).__init__()
            self.controller = controller
            self.dataModel = dataModel


                        
            
            numLines = self.dataModel.GetNumDatasets()
            self.controller.VisibleChanged.connect(self.SyncVisible)
            self.controller.LocationChanged.connect(self.SyncLocation)
            self.controller.ViewChanged.connect(self.SyncView)
            self.controller.NavModeChanged.connect(self.SyncNavMode)
            self.numDims = dataModel.GetNumDims()

            self.dataFnList = []
            if(self.numDims == 3):
                self.dataFnList = [self.dataModel.GetCurrXLine, self.dataModel.GetCurrYLine, self.dataModel.GetCurrZLine]
            elif(self.numDims == 2):
                self.dataFnList = [self.dataModel.GetCurrXLine, self.dataModel.GetCurrYLine]
                
            
            
            self.locations = []
            self.locationFnList = []
            self.markerFnList = []
            self.crossSection = []

            self.currLocation = dataModel.commonState.dimsTable['CurrLocation'].copy()
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(3)




            yLimits = ComputeYLimits(self.dataModel)

            self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

            
            for dimIndex in range(self.numDims):
                locations = np.arange(0, dataModel.GetDimValue(dimIndex, 'Shape'))
                self.locations.append(locations)

                self.locationFnList.append(lambda channel, dimIndex=dimIndex: self.locations[dimIndex])

                self.markerFnList.append(lambda channel, dimIndex=dimIndex: self.currLocation[dimIndex])

                visibleFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Visible')
                colorFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Color')
                crossSection = PlotPanel.PlotPanel(self.dataFnList[dimIndex],
                                                   self.locationFnList[dimIndex],
                                                   self.markerFnList[dimIndex],
                                                   dataModel.commonState.dimsTable.iloc[dimIndex],
                                                   numLines, colorFn, visibleFn, yLimits)
                
                crossSection.signalHoverOnLine.connect(lambda lineIndex, sampleIndex, dimIndex=dimIndex : self.controller.signalChangeSingleDimLocation.emit(dimIndex, sampleIndex))

                self.crossSection.append(crossSection)
                
                self.splitter.addWidget(crossSection)
                

            self.layout.addWidget(self.splitter)
        except Exception as err:
            Common.HandleException(err)
            

    def SyncVisible(self):
        yLimits = ComputeYLimits(self.dataModel)
        for cx in self.crossSection:
            cx.SyncYLimits(yLimits)
            cx.SyncVisible()
            
    def SyncLocation(self):
        try:

            somethingChanged = False
            for dimIndex in range(self.numDims):
                newLocation = self.dataModel.GetDimValue(dimIndex, 'CurrLocation')
                if self.currLocation[dimIndex] != newLocation:
                    self.currLocation[dimIndex] = newLocation
                    somethingChanged = True
            if somethingChanged:
                for dimIndex in range(self.numDims):
                    self.crossSection[dimIndex].SyncData(self.dataFnList[dimIndex])
                    
                    self.crossSection[dimIndex].SyncMarkers(self.markerFnList[dimIndex])
                                 
        except Exception as err:
            Common.HandleException(err)


    def SyncNavMode(self, mode):
        for cx in self.crossSection:
            cx.ChangeNavMode(mode)
            
    def SyncView(self):
        yLimits = ComputeYLimits(self.dataModel)

        for dimIndex in range(self.numDims):
            self.crossSection[dimIndex].SyncYLimits(yLimits)
            self.crossSection[dimIndex].SyncData(self.dataFnList[dimIndex])
            self.crossSection[dimIndex].SyncMarkers(self.markerFnList[dimIndex])
