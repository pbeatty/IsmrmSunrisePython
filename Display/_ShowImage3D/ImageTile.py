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
import numpy as np

from ..ImagePanelObjects import ImagePanel as ImagePanel


class ImageTile(QtWidgets.QFrame):
    """ wrapper class for ImagePanel

    """

    signalChangeLocation = QtCore.Signal(int,int)
    signalChangeWindowLevel = QtCore.Signal(float, float)
    signalScroll = QtCore.Signal(int)
    def __init__(self,
                 dim0Description,
                 dim1Description,
                 currViewFn,
                 dataFn):
        try:
            super(ImageTile, self).__init__()

            self.currViewFn = currViewFn
            
            self.setObjectName("ImageTile")
            self.setStyleSheet("ImageTile {padding: 0; margin: 0; border: 0;}")
            
            self.dataFn = dataFn

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)
            
            self.setSizePolicy(sizePolicy)
            
            self.panel = ImagePanel(dim0Description=dim0Description,
                                               dim1Description=dim1Description,
                                               currView=currViewFn(),
                                               imageData=dataFn())

            
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)
            self.layout.addWidget(self.panel)
            

            self.panel.signalChangeWindowLevel.connect(self.signalChangeWindowLevel)
            self.panel.signalChangeLocation.connect(self.signalChangeLocation)
            self.panel.signalScroll.connect(self.signalScroll)
        except Exception as err:
            print("Exception in ImageTile.__init__: {}".format(err))
            
    
    def ShowIt(self):
        self.panel.UpdateImageAndLines()

    def SyncNavMode(self, mode):
        self.panel.ChangeNavMode(mode)
        
    def SyncLocation(self, currLocation):
        try:
            self.panel.SetLocation(currLocation)

        except Exception as err:
            print("Exception in ImageTile.SyncLocation: {}".format(err))

    def SyncDataAndView(self):
        try:
            self.panel.SetImageData(self.dataFn())
            self.panel.SetView(self.currViewFn())

        except Exception as err:
            print("Exception in ImageTile.SyncDataAndView: {}".format(err))

    def SyncWindowLevel(self, window, level):
        self.panel.SetWindowLevel(window, level)
        self.ShowIt()
