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

from . import ControlWidget
from .. import Common
from ..ImagePanelObjects import PlotPanel
from . import DataModel as DataModel


def ComputeYLimits(dataModel):
    dataMin = dataModel.GetCurrViewValue('DataMin')
    dataMax = dataModel.GetCurrViewValue('DataMax')
    dataRange = dataMax-dataMin
    margin = dataRange * 0.05 + 0.001
    return [dataMin-margin, dataMax+margin]
    
class MainWindow(Common.MainWindow):
    def __init__(self, data, windowTitle):
        try:
            super(MainWindow,self).__init__()

            self.callingParams = {}
            self.callingParams['data'] = data.copy()
            self.callingParams['windowTitle'] = windowTitle
            
            self.dataModel = DataModel.DataModel(data)
            self.controller = Common.Controller(self.dataModel)

            if windowTitle is None:
                self.windowTitle = 'Display'
            else:
                self.windowTitle = windowTitle


            
            
            controlWidget = ControlWidget.ControlWidget(self.controller, self.dataModel)
            dataFn = lambda channel: self.dataModel.GetCurrDataSlice(channel)
            
            
            locationFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'SampleLocations')
            colorFn = lambda channel : self.dataModel.GetDataTableValue(channel, 'Color')
           
            self.markerFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'CurrIndex')
            self.visibleFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Visible')
            yLim = ComputeYLimits(self.dataModel)

            numLines = self.dataModel.GetNumDatasets()
            visibleFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Visible')
            colorFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Color')

            dimsTable = self.dataModel.commonState.dimsTable.iloc[0].copy()
            dimsTable['Color'] = Common.lightTextColor # don't need to color code border
            viewWidget=PlotPanel(dataFn=dataFn,
                                 locationFn=locationFn,
                                 markerFn=self.markerFn,
                                 dimsTable= dimsTable,
                                 numLines = numLines,
                                 colorFn = colorFn,
                                 visibleFn = visibleFn,
                                 yLimits=yLim)

            
            
            self.Setup(controlWidget, viewWidget)

            self.controller.LocationChanged.connect(self.SyncMarkers)
            self.controller.ViewChanged.connect(self.ChangeData)
            self.controller.NavModeChanged.connect(self.SyncNavMode)
            self.controller.VisibleChanged.connect(self.view.SyncVisible)
            self.controller.signalClone.connect(self.Clone)
                        
            
            self.view.signalHoverOnLine.connect(lambda lineIndex, sampleIndex: self.controller.signalChangeSingleLineLocation.emit(0, lineIndex, sampleIndex))
            
    
            self.setWindowTitle(windowTitle)
        except Exception as err:
            Common.HandleException(err)
                                                        
         

    def SyncMarkers(self):
        ''' Syncs view and controls with data model
        
        '''
        try:
            self.view.SyncMarkers(self.markerFn)
        except Exception as err:
            Common.HandleException(err)

    def SyncNavMode(self, mode):
        try:
            self.view.ChangeNavMode(mode)
        except Exception as err:
            Common.HandleException(err)    
    

    def ChangeData(self):
        try:

            dataFn = lambda channel: self.dataModel.GetCurrDataSlice(channel)   

            yLim = ComputeYLimits(self.dataModel)

            self.view.SyncYLimits(yLim)
            self.view.SyncData(dataFn)            
            self.SyncMarkers()
        except Exception as err:
            Common.HandleException(err)
        
    def Clone(self):
        try:
            viewer = MainWindow(**self.callingParams)
            viewer.Start()
        except Exception as err:
            Common.HandleException(err)
 
         
       
