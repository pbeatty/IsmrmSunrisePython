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

class TightVerticalLayout(QtWidgets.QVBoxLayout):
    def __init__(self, parent):
        super(TightVerticalLayout, self).__init__(parent)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
       
