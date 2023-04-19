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

__all__ = ["ViewBox"]

from qtpy import QtCore, QtWidgets
from .. import Common

class ViewBox(QtWidgets.QComboBox):
    """

    """
    def __init__(self, commonState, controller):
        try:
            super(ViewBox, self).__init__()
            self.commonState = commonState
            

            for viewIndex in self.commonState.viewsTable.index:
                self.addItem(self.commonState.viewsTable.loc[viewIndex, 'Name'])


                
            self.currentIndexChanged.connect(controller.signalChangeView)
            controller.ViewChanged.connect(self.Sync)
            
        except Exception as err:
            Common.HandleException(err)



    def Sync(self):
        """ Sync's widget values with model

        """
        try:
            self.setCurrentIndex(self.commonState.currViewIndex)
        except Exception as err:
            Common.HandleException(err)

