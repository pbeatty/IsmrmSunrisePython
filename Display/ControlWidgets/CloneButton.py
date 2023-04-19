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

from qtpy import QtCore, QtWidgets
from .. import Common


__all__ = ["CloneButton"]

class CloneButton(QtWidgets.QFrame):
    def __init__(self, controller):
        try:
            super(CloneButton, self).__init__()
            self.controller = controller
        
            self.layout = QtWidgets.QVBoxLayout(self)
            self.cButton = QtWidgets.QPushButton("Clone")
            self.cButton.setCheckable(False)
            self.layout.addWidget(self.cButton)
        
            self.cButton.pressed.connect(self.controller.signalClone)

            self.cButton.setStyleSheet("background-color: {};".format(Common.darkBackgroundColor))
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)
        except Exception as err:
            Common.HandleException(err)
