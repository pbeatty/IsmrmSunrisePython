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


class DataModel(Common.DataModel):
    def __init__(self, data):
        """ Stores a set of 1D complex functions

        Parameters
        ----------

        data : pandas data frame



        """
        try:

            self.locationSyncFlag = False
            
            if isinstance(data, pd.DataFrame):
                self.dataTable = data
            else:
                raise RuntimeError('data must be a DataFrame')
            
            dimShape = (1,)
            self.commonState = Common.CommonDataState(dimShape)
            self.SetMinMaxVisibleViewValues()

        except Exception as err:
            Common.HandleException(err)

    def GetCurrSampleIndex(self, datasetIndex):
        currIndex = int(self.GetDataTableValue(datasetIndex, 'CurrIndex'))
        return currIndex
        
    def GetCurrValue(self, datasetIndex):
        currIndex = int(self.GetDataTableValue(datasetIndex, 'CurrIndex'))
        return self.GetCurrDataSlice(datasetIndex,
                                     dim1Slice=currIndex)

    def GetCurrLocation(self, datasetIndex):
        currIndex = int(self.GetDataTableValue(datasetIndex, 'CurrIndex'))
        return self.GetDataTableValue(datasetIndex, 'SampleLocations')[currIndex]


    
