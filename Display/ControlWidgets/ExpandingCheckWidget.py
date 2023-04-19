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

__all__ = ["ExpandingCheckWidget"]

from qtpy import QtCore, QtWidgets

class ExpandingCheckWidget(QtWidgets.QFrame):
    """Widget with a check box at the top that shows/hides a widget below depending on whether or not it is checked
    
    Signals
    -------
    signalState : signals True if visible/checked, False if not visible/checked
    
    Members
    -------
    checkBox : top check box
    subWidget : the sub widget that is shown/hidden. 
    """
    signalState = QtCore.Signal(bool)
    
    
    def __init__(self, subWidget, title, color = None, initialState=True):
        """ Constructor
        
        Parameters
        ----------
        
        subWidget : widget that will be shown/hidden
        
        title : text beside check box
        
        color : a color can be given to identify this widget, shown on left border
        
        initialState : Whether to start off shown or hidden
        
        """
        try:
            super(ExpandingCheckWidget, self).__init__()
            
            self.checkBox = QtWidgets.QCheckBox(title)
            self.checkBox.setChecked(initialState)
    
            self.subWidget = subWidget
            
            # set up frame and style
            self.frame = QtWidgets.QGridLayout(self)
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setSpacing(0)
            self.setObjectName("ExpandingCheckWidget")
            
            if color is None:
                self.setStyleSheet("* {padding: 0; margin: 0; border: 0;} #ExpandingCheckWidget {border-width: 2px; border-style: none}")
            else:
                # double brackets {{ because of .format 
                self.setStyleSheet("* {{padding: 0; margin: 0; border: 0;}} #ExpandingCheckWidget {{border-width: 2px; border-color: {}; border-top-style: none; border-right-style: solid; border-bottom-style: none; border-left-style: solid}}".format(color))
            

            self.frame.addWidget(self.checkBox, 0, 0)
            self.frame.addWidget(self.subWidget, 1, 0)
            self.frame.setColumnStretch(1,1)
            self.subWidget.setVisible(initialState)
            
            self.checkBox.stateChanged.connect(self.ChangeState)
        except Exception as err:
            print('Exception in ExpandingCheckWidget.__init__: {}'.format(err))
        except:
            print('Unknown Exception')

    def ChangeState(self):
        try:            
            if self.checkBox.isChecked():
                self.subWidget.setVisible(True)
                self.signalState.emit(True)
            else:
                self.subWidget.setVisible(False)
                self.signalState.emit(False)
        
        except Exception as err:
            print('Exception in ExpandingCheckWidget.ChangeState: {} '.format(err))
        except:
            print('Unknown Exception')
