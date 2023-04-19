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

__all__ = ["DatasetLegendWidget"]

from qtpy import QtWidgets, QtCore
from .ScrollableContainerWidget import ScrollableContainerWidget
from .BasicValueBox import BasicValueBox

from .. import Common

class DatasetLegendWidget(ScrollableContainerWidget):
    def __init__(self, controller, dataModel):
        try:
            self.dataModel = dataModel
            self.controller = controller

            lineSelectLayout = QtWidgets.QVBoxLayout()
            self.lineBoxes = []
            for index in range(dataModel.GetNumDatasets()):
                im = dataModel.GetDataTableValue(index)

                currValueBox = BasicValueBox(lambda index=index: self.dataModel.GetCurrValue(index), self.dataModel.GetDataTableValue(index, 'Title'), self.dataModel.GetDataTableValue(index, 'Color'));

                currValueBox.signalState.connect(lambda visibleFlag, index=index : self.controller.signalChangeVisible.emit(index, visibleFlag)) 
                self.lineBoxes.append(currValueBox)
                lineSelectLayout.addWidget(self.lineBoxes[index])

                self.controller.LocationChanged.connect(currValueBox.UpdateValues)
                self.controller.ViewChanged.connect(currValueBox.UpdateValues)
                
            lineSelectLayout.addStretch(10)
            
            super(DatasetLegendWidget, self).__init__(lineSelectLayout)

            
        except Exception as err:
            Common.HandleException(err)
    
    
