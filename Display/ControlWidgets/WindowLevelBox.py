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

from qtpy import QtWidgets, QtCore
from IPython.display import display

__all__ = ["WindowLevelBox"]

class WindowLevelBox(QtWidgets.QFrame):
    """
    Widget with Window and Level boxes

    Initialized with a commonState that must have window and level members

    Emits commonSignals.signalChangeWindowLevel when user changes window or level in widget

    Call Sync member cases widget to update values based on commonState
    """
    
    def __init__(self, commonState, controller):
        try:
            super(WindowLevelBox, self).__init__()
            self.commonState = commonState
            self.controller = controller

            self.controller.WindowLevelChanged.connect(self.Sync)
            self.controller.ViewChanged.connect(self.Sync)
            
            self.frame = QtWidgets.QGridLayout(self)
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setSpacing(0)

            self.setStyleSheet("* {padding: 0px; margin: 0px; border: 0px;}")

            
            self.windowLabel = QtWidgets.QLabel()
            self.windowLabel.setText("W")
            self.window = QtWidgets.QDoubleSpinBox()
            self.window.setMinimum(-1.0)
            self.window.setMaximum(10.0**100)
            self.window.setDecimals(3)
            self.window.setMaximumWidth(70)                        
            self.window.setValue(self.commonState.GetCurrViewValue('Window'))            
                        
            self.levelLabel = QtWidgets.QLabel()
            self.levelLabel.setText("L")
            self.level = QtWidgets.QDoubleSpinBox()
            self.level.setMinimum(-10.0**100)
            self.level.setMaximum(10.0**100)
            self.level.setDecimals(3)
            self.level.setMaximumWidth(70)                        
            self.level.setValue(self.commonState.GetCurrViewValue('Level'))
            
            self.frame.addWidget(self.windowLabel, 0, 0, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(self.window, 0, 1, alignment=QtCore.Qt.AlignLeft)
            self.frame.addWidget(self.levelLabel, 1,0, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(self.level, 1,1, alignment=QtCore.Qt.AlignLeft)

            # connect signal and slots
            self.window.valueChanged.connect(self._ChangeWindow)
            self.level.valueChanged.connect(self._ChangeLevel)
            
        except Exception as err:
            print('Exception in WindowLevelBox.__init__: {}'.format(err))

    def _ChangeWindow(self, window):
        try:
            if( window != self.commonState.GetCurrViewValue("Window")):
                self.controller.signalChangeWindowLevel.emit(window, self.commonState.GetCurrViewValue('Level'))
        except Exception as err:
            print('Exception in WindowLevelBox.ChangeWindow: ', err)
        

    def _ChangeLevel(self, level):
        try:
            if( level != self.commonState.GetCurrViewValue("Level")):
                self.controller.signalChangeWindowLevel.emit(self.commonState.GetCurrViewValue('Window'), level)
        except Exception as err:
            print('Exception in WindowLevelBox.ChangeLevel: ', err)
            
    def Sync(self):
        """ Sync's widget values with model
        
        """
        try:

            window = self.commonState.GetCurrViewValue("Window")
            level = self.commonState.GetCurrViewValue("Level")

            self.window.setValue(window)
            self.level.setValue(level)

            isEnabled = self.commonState.GetCurrViewValue("EnableWindowLevelChange")
            self.window.setEnabled(isEnabled)
            self.level.setEnabled(isEnabled)
            
        except Exception as err:
            print('Exception in WindowLevelBox.ChangeLevel: ', err)
