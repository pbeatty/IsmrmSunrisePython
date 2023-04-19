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
import numpy as np
import pandas as pd
import matplotlib.cm as colormaps
from IPython.display import display

from qtpy import QtCore
from .. import Common





class DataModel(Common.ShowImageDataModel):



    def GetCurrValue(self, datasetIndex):
        return self.GetCurrDataSlice(datasetIndex,
                                dim1Slice=self.GetDimValue(0, 'CurrLocation'),
                                dim2Slice=self.GetDimValue(1, 'CurrLocation'),
                                dim3Slice=self.GetDimValue(2, 'CurrLocation'))

    def GetCurrXLine(self, datasetIndex):
        return self.GetCurrDataSlice(datasetIndex,
                                dim2Slice=self.GetDimValue(1, 'CurrLocation'),
                                dim3Slice=self.GetDimValue(2, 'CurrLocation'))

    def GetCurrYLine(self, datasetIndex):
        return self.GetCurrDataSlice(datasetIndex,
                                dim1Slice=self.GetDimValue(0, 'CurrLocation'),
                                dim3Slice=self.GetDimValue(2, 'CurrLocation'))

    
    def GetCurrZLine(self, datasetIndex):
        return self.GetCurrDataSlice(datasetIndex,
                                dim1Slice=self.GetDimValue(0, 'CurrLocation'),
                                dim2Slice=self.GetDimValue(1, 'CurrLocation'))
    def GetCurrXYPlane(self, datasetIndex):
        return self.GetCurrDataSlice(datasetIndex,
                                dim3Slice=self.GetDimValue(2, 'CurrLocation'))
                      
    def GetCurrYZPlane(self, datasetIndex):
        xLoc = self.GetDimValue(0, 'CurrLocation')
        rv = self.GetCurrDataSlice(datasetIndex,
                                   dim1Slice=xLoc)
        return rv
    def GetCurrZXPlane(self, datasetIndex):
        return np.transpose(self.GetCurrDataSlice(datasetIndex,
                                dim2Slice=self.GetDimValue(1, 'CurrLocation')))
                                
