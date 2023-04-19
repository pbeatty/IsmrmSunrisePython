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
from .OrthoImagePanel import OrthoImagePanel
from ..ImagePanelObjects import CrossSections
from .. import Common
import numpy as np

class ViewPanel(QtWidgets.QFrame):

    def __init__(self,
                 controller,
                 dataModel):
        try:

            super(ViewPanel, self).__init__()

            self.controller = controller
            self.dataModel = dataModel

            self.orthoImagePanel = OrthoImagePanel(self.controller, self.dataModel)            

            self.crossSections = CrossSections(self.controller, self.dataModel)

            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)
            self.splitter = QtWidgets.QSplitter()

            self.splitter.addWidget(self.orthoImagePanel)
            self.splitter.addWidget(self.crossSections)

            self.layout.addWidget(self.splitter)

        except Exception as err:
            Common.HandleException(err)

