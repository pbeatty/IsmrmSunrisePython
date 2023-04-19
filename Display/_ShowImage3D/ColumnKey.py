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
from IPython.display import display
from .. import Common
from .ImageTile import ImageTile 
class ColumnKey(QtWidgets.QFrame):
    """ Displays similarly sized images

    """
    def __init__(self, title, dataModel, width):

        ''' Constructor

        Parameters
        ----------
        '''
        try:
            self.dataModel = dataModel
            self.visibleFn = lambda channel: self.dataModel.GetDataTableValue(channel, 'Visible')

            super(ColumnKey, self).__init__()
            self.setMinimumWidth(width)
            self.setMaximumWidth(width)
            
            self.setObjectName("ColumnKey")
            self.setStyleSheet("* {padding: 0; margin: 0; border: 0;}")

            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(3)
            self.numImages = self.dataModel.GetNumDatasets()


            self.frameList = []
            self.visibleIndices = []

            rowOffset = 0
            if title is not None:
                self.titleLabel = QtWidgets.QLabel()
                self.titleLabel.setText(title)
                self.titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.titleLabel.setMinimumHeight(20)
                self.titleLabel.setMaximumHeight(20)
                self.layout.addWidget(self.titleLabel)
                rowOffset = 1
            
            for imIndex in range(self.numImages):

                currColor = dataModel.GetDataTableValue(imIndex, 'Color')
                
                panel = QtWidgets.QFrame()
                panel.setMinimumHeight(10)
                panel.setObjectName("keyPanel")
                panel.setStyleSheet("#keyPanel {{padding: 0; margin: 0; border: 0; background-color: {};}}".format(currColor))
            
                
                self.frameList.append(panel)
                self.layout.addWidget(panel)
                self.visibleIndices.append(imIndex)

        except Exception as err:
            Common.HandleException(err)

    def SetRowHeight(self, height):
        for index in self.visibleIndices:
            frame = self.frameList[index]
            frame.setMinimumHeight(height)
            frame.setMaximumHeight(height)
            frame.resize(frame.width(), height)
            
            
    def SyncVisible(self):
        """ synchronizes which plots are displayed with visibleFn

        visibleFn : lambda, takes image index and returns True/False
        """
        try:

            for imIndex in reversed(self.visibleIndices):
                self.layout.removeWidget(self.frameList[imIndex])
                self.frameList[imIndex].hide()
            
            numVisible = 0
            self.visibleIndices = []
            for imIndex in range(self.numImages):
                if self.visibleFn(imIndex):
                    numVisible += 1
                    self.visibleIndices.append(imIndex)
                    

            for visibleIndex in range(numVisible):
                imIndex = self.visibleIndices[visibleIndex]
                currFrame = self.frameList[imIndex]
                self.layout.addWidget(currFrame)
                currFrame.show()

        except Exception as err:
            Common.HandleException(err)
