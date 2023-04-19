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

from .ImageGrid import ImageGrid
from .. import Common


class ImagesPanel(QtWidgets.QFrame):
    """ Displays of grid of similarly sized images

    """
    
    def __init__(self, controller, dataModel):
        ''' Constructor

        Parameters
        ----------
        '''
        try:
            super(ImagesPanel, self).__init__()


            self.imageGrid = ImageGrid(controller, dataModel, None)
             
            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidget(self.imageGrid)
            self.scroll.setWidgetResizable(True)
            self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)            
            self.layout.addWidget(self.scroll)
            
            self.setLayout(self.layout)
            self.imageGrid.signalScroll.connect(self.Scroll)


        except Exception as err:
            Common.HandleException(err)

    def resizeEvent(self, e):
        self.imageGrid.SetWidth(self.scroll.viewport().width())
            
    def Scroll(self, amount):
        val = self.scroll.verticalScrollBar().value()
        self.scroll.verticalScrollBar().setValue(val+100*amount)


    def sizeHint(self):
        return QtCore.QSize(700,800)
