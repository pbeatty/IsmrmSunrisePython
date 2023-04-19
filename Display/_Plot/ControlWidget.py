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
from .. import ControlWidgets
from .. import Common

class ControlWidget(QtWidgets.QFrame):
    
    def __init__(self, controller, dataModel):
        try:
            super(ControlWidget, self).__init__()
            self.controller = controller
            self.dataModel = dataModel

            layout = QtWidgets.QVBoxLayout(self)

            # Clone Button
            self.cloneButton = ControlWidgets.CloneButton(self.controller)
            layout.addWidget(self.cloneButton)
            
            # Image Type combo box (Magnitude/Phase/Real/Imaginary)
            self.viewBox = ControlWidgets.ViewBox(self.dataModel.commonState, self.controller)
            layout.addWidget(self.viewBox)

            # Inspect/Zoom/Pan combo box
            self.navMode = ControlWidgets.NavModeBox(self.controller)
            layout.addWidget(self.navMode)

            #Sync locations
            self.syncLocationCheckBox = QtWidgets.QCheckBox("Sync Locations")
            layout.addWidget(self.syncLocationCheckBox)
            self.syncLocationCheckBox.stateChanged.connect(lambda state : self.controller.signalChangeLocationSync.emit(state>0))
            
            
            #Check boxes for plots
            lineSelectLayout = QtWidgets.QVBoxLayout()
            self.lineBoxes = []
            dimName = self.dataModel.GetDimValue(0, 'Name')
            for index in range(self.dataModel.GetNumDatasets()):
                GetDataValue = lambda columnName, index=index : self.dataModel.GetDataTableValue(index, columnName)
                dataLine = self.dataModel.GetDataTableValue(index)

                color = self.dataModel.GetDataTableValue(index, 'Color')
                title = self.dataModel.GetDataTableValue(index, 'Title')
                getCurrSampleIndexFn = lambda index=index: self.dataModel.GetCurrSampleIndex(index)
                getCurrValueFn = lambda index=index : self.dataModel.GetCurrValue(index)
                getCurrLocationFn = lambda index=index: self.dataModel.GetCurrLocation(index)

                maxIndex = self.dataModel.GetDataTableValue(index,'Data').shape[0]-1
                currLineBox = ControlWidgets.LineBox(getCurrSampleIndexFn,
                                                     getCurrValueFn,
                                                     getCurrLocationFn,
                                                     index,
                                                     dimName,
                                                     title,
                                                     color,
                                                     maxIndex,
                                                     self.controller)
                self.lineBoxes.append(currLineBox)
                lineSelectLayout.addWidget(currLineBox)
                self.controller.LocationChanged.connect(currLineBox.UpdateValues)
                self.controller.ViewChanged.connect(currLineBox.UpdateValues)
                
            lineSelectLayout.addStretch(10)
            
            layout.addWidget(ControlWidgets.ScrollableContainerWidget(lineSelectLayout))


            
        except Exception as err:
            Common.HandleException(err)
        
        
            
        
        
        
