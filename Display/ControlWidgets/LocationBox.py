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

from qtpy import QtCore, QtWidgets
from .. import Common

__all__ = ["LocationBox"]


class LocationBox(QtWidgets.QFrame):
    """
    
    
    """

    def __init__(self, commonState, controller):
        try:
            super(LocationBox, self).__init__()

            self.commonState = commonState
            self.controller = controller
            controller.signalChangeSingleDimLocation.connect(self.Sync)
            controller.signalChangeDoubleDimLocation.connect(self.Sync)
            
            self.frame = QtWidgets.QGridLayout(self)
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setSpacing(0)

            self.setStyleSheet("* {padding: 0px; margin: 0px; border: 0px;}")

            self.dimLabels = []
            self.dimLocations = []
            
            for dimIndex in commonState.dimsTable.index:

                dimName = commonState.GetDimValue(dimIndex, 'Name')
                dimExtent = commonState.GetDimValue(dimIndex,'Shape')

                
                dimLabel = QtWidgets.QLabel()
                
                dimLabel.setText(dimName)
                dimLocation = QtWidgets.QSpinBox()
                dimLocation.setMinimum(0)
                dimLocation.setMaximum(dimExtent-1)

                self.frame.addWidget(dimLabel, dimIndex, 0, alignment=QtCore.Qt.AlignRight)
                self.frame.addWidget(dimLocation, dimIndex, 1, alignment=QtCore.Qt.AlignLeft)

                dimLocation.valueChanged.connect(lambda idx, dimIndex=dimIndex : self.ChangeIndex(dimIndex, idx))

                self.dimLabels.append(dimLabel)
                self.dimLocations.append(dimLocation)
                
            
        except Exception as err:
            Common.HandleException(err)

    def ChangeIndex(self, dimIndex, index):
        if index != self.commonState.GetDimValue(dimIndex, 'CurrLocation'):
            self.controller.signalChangeSingleDimLocation.emit(dimIndex, index)

    def Sync(self):
        for dimIndex in self.commonState.dimsTable.index:
            self.dimLocations[dimIndex].setValue(self.commonState.GetDimValue(dimIndex, 'CurrLocation'))
