"""
A collection of classes that are widget building blocks for display control panels

Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Alan Kuurstra
Philip J. Beatty (philip.beatty@gmail.com)

2017, modified by Chad Harris
2017, modified by Philip Beatty
"""

__all__ = ["LineBox"]

from qtpy import QtCore, QtWidgets
from .ExpandingCheckWidget import *
from .InspectOneDimWidget import InspectOneDimWidget

from .. import Common

class LineBox(ExpandingCheckWidget):
    def __init__(self,
                 getCurrSampleIndexFn,
                 getCurrValueFn,
                 getCurrLocationFn,
                 idIndex,
                 dimName,
                 title,
                 color,
                 maxIndex,
                 controller):
        try:
            self.idIndex = idIndex
            self.controller = controller
            subWidget = InspectOneDimWidget(getCurrSampleIndexFn, getCurrValueFn, getCurrLocationFn, dimName, maxIndex)
            super(LineBox, self).__init__(subWidget, title, color)

            self.signalState.connect(self.ChangeVisible)
            subWidget.signalIndexChange.connect(self.ChangeLocationIndex)
        except Exception as err:
            Common.HandleException(err)

    def ChangeVisible(self, state):
        try:
            self.controller.signalChangeVisible.emit(self.idIndex, state)
        except Exception as err:
            Common.HandleException(err)

    def ChangeLocationIndex(self, index):
        try:
            self.controller.signalChangeSingleLineLocation.emit(0, self.idIndex, index)
        except Exception as err:
            Common.HandleException(err)

           
    def UpdateValues(self):
        self.subWidget.UpdateValues()

