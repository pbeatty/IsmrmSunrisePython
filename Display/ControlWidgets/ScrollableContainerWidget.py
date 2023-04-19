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

__all__ = ["ScrollableContainerWidget"]
from qtpy import QtCore, QtWidgets

class ScrollableContainerWidget(QtWidgets.QFrame):
    def __init__(self, subLayout):
        try:
            super(ScrollableContainerWidget, self).__init__()
            self.containerWidget = QtWidgets.QFrame()            
            self.containerWidget.setLayout(subLayout)        

            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidget(self.containerWidget)
            self.scroll.setWidgetResizable(True)
            self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)            
            self.layout.addWidget(self.scroll)
            
            self.setLayout(self.layout)
            
        except Exception as err:
            print('Exception: ', err)
                     
            
    def showEvent(self, ev):
        super(ScrollableContainerWidget, self).showEvent(ev)
        containerWidth = self.scroll.widget().sizeHint().width()
        scrollWidth = self.scroll.verticalScrollBar().sizeHint().width()
        
        self.scroll.setMinimumWidth(containerWidth + scrollWidth)

