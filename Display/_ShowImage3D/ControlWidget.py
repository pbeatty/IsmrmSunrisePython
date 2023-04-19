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


            # Window/Level Box
            self.windowLevelBox = ControlWidgets.WindowLevelBox(self.dataModel.commonState,
                                                                self.controller)
            layout.addWidget(self.windowLevelBox)


            
            # add index location changer                
            self.locationBox = ControlWidgets.LocationBox(self.dataModel.commonState,
                                                          self.controller)
            layout.addWidget(self.locationBox)

            #Check boxes for plots
            layout.addWidget(ControlWidgets.DatasetLegendWidget(self.controller, self.dataModel))

            
        except Exception as err:
            Common.HandleException(err)


    def sizeHint(self):
        return QtCore.QSize(100,800)

    
