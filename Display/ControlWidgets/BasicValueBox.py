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

__all__ = ["BasicValueBox"]

from .ExpandingCheckWidget import *
from .InspectValueWidget import InspectValueWidget


class BasicValueBox(ExpandingCheckWidget):
    def __init__(self, getCurrValueFn, title, color):
        try:

            subWidget = InspectValueWidget(getCurrValueFn)    
            super(BasicValueBox, self).__init__(subWidget, title, color)

        except Exception as err:
            print("Exception in BasicValueBox.__init__: {}".format(err))

    def UpdateValues(self):
        self.subWidget.UpdateValues()
