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

__all__ = ["InspectValueWidget"]

from qtpy import QtCore, QtWidgets

class InspectValueWidget(QtWidgets.QFrame):
    """ Shows current value
    """
    def __init__(self, getCurrValueFn):
        """

        Parameters
        ----------

        getCurrValueFn : a function/lambda with no argumnents that
        returns the current value to display

        """
        try:
            super(InspectValueWidget, self).__init__()
    
            self.getCurrValueFn = getCurrValueFn              
            
            self.frame = QtWidgets.QGridLayout(self)
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setSpacing(0)
            self.setStyleSheet("* {padding: 0px; margin: 0px; border: 0px;}")
            
            self.valueLabel = QtWidgets.QLabel()
            self.valueLabel.setText("Value:")
            self.value = QtWidgets.QLabel()
            self.UpdateValues()        
            
            
            self.frame.addWidget(self.valueLabel, 0,0, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(self.value, 0,1, alignment=QtCore.Qt.AlignLeft)
            
        except Exception as err:
            print('Exception in InspectValueWidget.__init__: {}'.format(err))
        except:
            print('Unknown Exception')
        
            

    def UpdateValues(self):
        try:
            currValue = self.getCurrValueFn()
            self.value.setText("{0:.4g}".format(currValue))
            
        except Exception as err:
            print('Exception in InspectValueWidget.UpdateValues: {}'.format(err))
        except:
            print('Unknown Exception')
