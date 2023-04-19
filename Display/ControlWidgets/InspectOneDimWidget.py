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

__all__ = ["InspectOneDimWidget"]

from qtpy import QtCore, QtWidgets


class InspectOneDimWidget(QtWidgets.QFrame):
    """ Shows index, x and y values
    
    Signals
    -------
    signalIndexChange : signals new index value, if changed in gui

    """    
    signalIndexChange = QtCore.Signal(int)
   
    def __init__(self, getCurrSampleIndexFn, getCurrValueFn, getCurrLocationFn,  dimName, maxIndex):
        try:
            super(InspectOneDimWidget, self).__init__()
            
            self.getCurrSampleIndexFn = getCurrSampleIndexFn
            self.getCurrValueFn = getCurrValueFn
            self.getCurrLocationFn = getCurrLocationFn


            
            self.frame = QtWidgets.QGridLayout(self)
            self.frame.setContentsMargins(0,0,0,0)
            self.frame.setSpacing(0)
            self.setStyleSheet("* {padding: 0; margin: 0; border: 0;}")
            self.locationLabel = QtWidgets.QLabel()
            self.locationLabel.setText("Index:")
            self.locationIndex = QtWidgets.QSpinBox()
            self.locationIndex.setMinimum(0)
            self.locationIndex.setMaximum(maxIndex)
            self.xLabel = QtWidgets.QLabel()
            self.xLabel.setText("{}:".format(dimName))
            self.xValue = QtWidgets.QLabel()

            self.valueLabel = QtWidgets.QLabel()
            self.valueLabel.setText("Value:")
            self.valueValue = QtWidgets.QLabel()


            self.UpdateValues()        
            
            # add component widgets to frame
            self.frame.addWidget(self.locationLabel, 0, 0, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(self.locationIndex, 0, 1, alignment=QtCore.Qt.AlignLeft)
            self.frame.addWidget(self.xLabel, 1,0, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(self.xValue, 1,1, alignment=QtCore.Qt.AlignLeft)
            self.frame.addWidget(self.valueLabel, 2,0, alignment=QtCore.Qt.AlignRight)
            self.frame.addWidget(self.valueValue, 2,1, alignment=QtCore.Qt.AlignLeft)        
            
            # connect signal and slots
            self.locationIndex.valueChanged.connect(self.ChangeLocationIndex)
        except Exception as err:
            print('Exception in InspectOneDimWidget.__init: {}'.format(err))
        except:
            print('Unknown Exception')
        
    
    def ChangeLocationIndex(self, index):
        self.signalIndexChange.emit(index)

    def UpdateValues(self):
        try:
            sampleIndex = self.getCurrSampleIndexFn()
            self.locationIndex.setValue(sampleIndex)
            valueValue = self.getCurrValueFn()
            xValue = self.getCurrLocationFn()
                                                                
            self.xValue.setText("{0:.4g}".format(xValue))
            self.valueValue.setText("{0:.4g}".format(valueValue))
        except Exception as err:
            print('Exception in InspectOneDimWidget.UpdateValues: {} '.format(err))
        except:
            print('Unknown Exception')
