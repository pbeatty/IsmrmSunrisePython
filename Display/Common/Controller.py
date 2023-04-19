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

__all__ = ["Controller"]

from qtpy import QtCore
from . import DisplayCore
from IPython.display import display


class Controller(QtCore.QObject):
    signalChangeNumCols = QtCore.Signal(int)
    signalChangeVisible = QtCore.Signal(int, bool)

    signalChangeSingleLineLocation = QtCore.Signal(int, int, int) # dimIndex, lineIndex, sampleIndex
    signalChangeLocationSync = QtCore.Signal(bool)
    
    signalChangeSingleDimLocation = QtCore.Signal(int, int)
    signalChangeDoubleDimLocation = QtCore.Signal(int, int, int, int)
    signalChangeWindowLevel = QtCore.Signal(float, float)
    signalChangeNavMode = QtCore.Signal(int)
    signalChangeView = QtCore.Signal(int)
    signalClone = QtCore.Signal()
    
    VisibleChanged = QtCore.Signal()
    LocationChanged = QtCore.Signal()
    WindowLevelChanged = QtCore.Signal()
    ViewChanged = QtCore.Signal()
    NavModeChanged = QtCore.Signal(str)

    def __init__(self, dataModel):
        try:
            super(Controller, self).__init__()
            
            self.dataModel = dataModel
            self.signalChangeVisible.connect(self.ChangeVisible)

            self.signalChangeLocationSync.connect(self.ChangeLocationSync)
            self.signalChangeSingleLineLocation.connect(self.ChangeSingleLineLocation)
            self.signalChangeSingleDimLocation.connect(self.ChangeSingleDimLocation)
            self.signalChangeDoubleDimLocation.connect(self.ChangeDoubleDimLocation)
            
            self.signalChangeWindowLevel.connect(self.ChangeWindowLevel)
            self.signalChangeNavMode.connect(self.ChangeNavMode)
            self.signalChangeView.connect(self.ChangeView)

            
        except Exception as err:
            DisplayCore.HandleException(err)
            
    def ChangeVisible(self, index, visibleFlag):
        ''' Propogates visibility to view
        
        '''
        try:
            self.dataModel.dataTable.iloc[index, self.dataModel.dataTable.columns.get_loc('Visible')] = visibleFlag
            self.dataModel.SetMinMaxVisibleViewValues()
            self.VisibleChanged.emit()
        except Exception as err:
            DisplayCore.HandleException(err)


    def ChangeSingleLineLocation(self, dimIndex, lineIndex, sampleIndex):
        try:

            if self.dataModel.locationSyncFlag == True:
                self.dataModel.dataTable['CurrIndex'] = sampleIndex
            else:
                self.dataModel.dataTable.iloc[lineIndex, self.dataModel.dataTable.columns.get_loc('CurrIndex')] = sampleIndex

            self.LocationChanged.emit()
        except Exception as err:
            DisplayCore.HandleException(err)

    def ChangeLocationSync(self, syncFlag):
        try:
            self.dataModel.locationSyncFlag = syncFlag
            self.LocationChanged.emit()
            
        except Exception as err:
            DisplayCore.HandleException(err)
    
    def ChangeSingleDimLocation(self, dimIndex, sampleIndex):
        try:

            self.dataModel.commonState.dimsTable.iloc[dimIndex, self.dataModel.commonState.dimsTable.columns.get_loc('CurrLocation')] = sampleIndex
            self.LocationChanged.emit()
        except Exception as err:
            DisplayCore.HandleException(err)



    def ChangeDoubleDimLocation(self, dim1Index, sample1Index, dim2Index, sample2Index):
        try:

            currLocationIndex = self.dataModel.commonState.dimsTable.columns.get_loc('CurrLocation')
            self.dataModel.commonState.dimsTable.iloc[dim1Index, currLocationIndex] = sample1Index
            self.dataModel.commonState.dimsTable.iloc[dim2Index, currLocationIndex] = sample2Index
            self.LocationChanged.emit()
        except Exception as err:
            DisplayCore.HandleException(err)

    def ChangeWindowLevel(self, window, level):
        try:
            currViewIndex = self.dataModel.commonState.currViewIndex

            self.dataModel.commonState.viewsTable.iloc[currViewIndex, self.dataModel.commonState.viewsTable.columns.get_loc('Window')] = window
            self.dataModel.commonState.viewsTable.iloc[currViewIndex, self.dataModel.commonState.viewsTable.columns.get_loc('Level')] = level
            self.WindowLevelChanged.emit()
        
        except Exception as err:
            DisplayCore.HandleException(err)
            
    def ChangeNavMode(self, mode):
        '''
        Called when controls change nav mode (Inspect, Zoom, Pan)
        
        Parameters
        ----------
        
        mode : 0 = Inspect, 1 = Zoom, 2 = Pan
        '''
        try:
            if mode == 0:
                modeString = 'INSPECT'
            elif mode == 1:
                modeString = 'ZOOM'
            elif mode == 2:
                modeString = 'PAN'

            self.NavModeChanged.emit(modeString)
        except Exception as err:
            DisplayCore.HandleException(err)

      
    def ChangeView(self, imType):
        try:
            self.dataModel.commonState.currViewIndex = imType
            self.ViewChanged.emit()
        except Exception as err:
            DisplayCore.HandleException(err)

