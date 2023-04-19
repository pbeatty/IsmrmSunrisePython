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


__all__ = ["NavModeBox"]

class NavModeBox(QtWidgets.QComboBox):
    def __init__(self, controller):
        try:
            super(NavModeBox, self).__init__()

            self.addItem("Investigate")
            self.addItem("Zoom")
            self.addItem("Pan")

            self.currentIndexChanged.connect(controller.signalChangeNavMode)

        except Exception as err:
            Common.HandleException(err)
