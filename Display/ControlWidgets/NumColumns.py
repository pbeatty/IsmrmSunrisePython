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

__all__ = ["NumColumns"]


class NumColumns(QtWidgets.QFrame):
    """
    
    
    """

    def __init__(self, controller, startValue = 1, maxNumColumns=10):
        try:
            super(NumColumns, self).__init__()

            self.controller = controller
            
            self.frame = QtWidgets.QHBoxLayout(self)
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setSpacing(0)

            self.setStyleSheet("* {padding: 0px; margin: 0px; border: 0px;}")

                
            label = QtWidgets.QLabel()
                
            label.setText('# Columns')
            numCols = QtWidgets.QSpinBox()
            numCols.setMinimum(1)
            numCols.setMaximum(maxNumColumns)

            self.frame.addWidget(label, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(numCols, alignment=QtCore.Qt.AlignLeft)

            numCols.valueChanged.connect(self.controller.signalChangeNumCols)
            numCols.setValue(startValue)
        except Exception as err:
            Common.HandleException(err)
