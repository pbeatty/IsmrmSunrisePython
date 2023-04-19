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
from .. import Common
from qtpy import QtWidgets, QtCore

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
                 dataFn, title, color):
        try:
            super(ImageTile, self).__init__()

            self.aspectRatio =  dim1Description.get('Shape') * (1.0/dim0Description.get('Shape'))
            
            self.titleHeight = 15
            self.oldWidth = -1
            
            self.currViewFn = currViewFn

            self.title = title
            
            self.setObjectName("ImageTile")
            self.setStyleSheet("#ImageTile {padding: 0; margin: 0; border-width: 0; background-color: #000000;}")
            
            self.dataFn = dataFn

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

            
            self.setSizePolicy(sizePolicy)

            self.colorPanel = QtWidgets.QLabel()
            self.colorPanel.setAlignment(QtCore.Qt.AlignCenter)
            self.colorPanel.setText(title)
            self.colorPanel.setMinimumHeight(self.titleHeight)
            self.colorPanel.setMaximumHeight(self.titleHeight)
            self.colorPanel.setObjectName("colorPanel")
            self.colorPanel.setStyleSheet("#colorPanel {{padding: 0; margin: 0; border-width: 0; background-color: {};color: {}}}".format(color, Common.darkBackgroundColor))
            self.panel = ImagePanel(dim0Description=dim0Description,
                                               dim1Description=dim1Description,
                                               currView=currViewFn(),
                                               imageData=dataFn())
            
            
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)

            
            self.layout.addWidget(self.colorPanel)
            self.layout.addWidget(self.panel)
            

            self.panel.signalChangeWindowLevel.connect(self.signalChangeWindowLevel)
            self.panel.signalChangeLocation.connect(self.signalChangeLocation)
            self.panel.signalScroll.connect(self.signalScroll)
        except Exception as err:
            Common.HandleException(err)


    def SetWidth(self, width):
        height = int(self.aspectRatio * width + self.titleHeight)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.ShowIt()
        
    def ShowIt(self):
        self.panel.UpdateImageAndLines()

    def SyncNavMode(self, mode):
        self.panel.ChangeNavMode(mode)
        
    def SyncLocation(self, currLocation):
        try:
            self.panel.SetLocation(currLocation)
        except Exception as err:
            Common.HandleException(err)

    def SyncDataAndView(self):
        try:
            self.panel.SetImageData(self.dataFn())
            self.panel.SetView(self.currViewFn())

        except Exception as err:
            Common.HandleException(err)

    def SyncWindowLevel(self, window, level):
        self.panel.SetWindowLevel(window, level)
        self.ShowIt()
