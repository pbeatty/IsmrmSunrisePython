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

#
# Objective of these factories is to provide convenience functions for creating data in pandas DataFrame format
#

import numpy as np
import pandas as pd
from .. import Common

def CreateDataFrameFromLists(complexDataList, sampleLocationsList, titleList=None):
    
    
    numRows = len(complexDataList)

    colors = Common.MakeColors(numRows)
    if len(sampleLocationsList) != numRows:
        raise RuntimeError("complexDataList length({}) does not match sampleLocationsList length ({})".format(numRows, len(sampleLocationList)))
    
    dataTable = pd.DataFrame(columns=('Title', 'Data', 'SampleLocations', 'Color', 'CurrIndex', 'Visible', 'Index'))

    if titleList is None:
        titleList = []
        for index in range(numRows):
            titleList.append("Index {}".format(index))
    
    for index in range(numRows):

        dataLength = complexDataList[index].shape[0]
        locationLength = sampleLocationsList[index].shape[0]
        if dataLength != locationLength:
            raise RuntimeError("for index {}: dataLength ({}) != locationLength ({})".format(index, dataLength, locationLength))
        
        
        newRow = {
            'Title' : titleList[index],
            'Data' : complexDataList[index],
            'SampleLocations': sampleLocationsList[index],
            'Color' : colors[index],
            'CurrIndex': 0,
            'Visible': True,
            'Index': index
            }
    
        dataTable.loc[index] = newRow
    return dataTable
