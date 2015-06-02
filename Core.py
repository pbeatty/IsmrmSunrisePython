"""
Notes
-----
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
Philip J. Beatty (philip.beatty@gmail.com)    
"""


import numpy as np

class TransformDirection:
    FORWARD=1492
    BACKWARD=1969


def MakeGrid(shape, step=None, start=None): 

    if step==None:
        step = np.ones(2)

    # if start not specified, we'll arrange it as assumed in fftshift    
    if start==None:
        start = np.zeros(2)
        if shape[0] % 2:
            start[0] = -0.5 * (shape[0]-1) * step[0]
        else:
            start[0] = -0.5 * (shape[0]) * step[0]
        if shape[1] % 2:    
            start[1] = -0.5 * (shape[1]-1) * step[1]
        else:
            start[1] = -0.5 * shape[1] * step[1]
                        
    
    x = np.arange(0, shape[0]) * step[0] + start[0]
    y = np.arange(0, shape[1]) * step[1] + start[1]
    
    xGrid, yGrid = np.meshgrid(x, y)
    xGrid = np.asfortranarray(xGrid.T)
    yGrid = np.asfortranarray(yGrid.T)
    
    return xGrid, yGrid    


def FlattenArrayList(aList, dtype=np.complex64):
    flatArray = np.zeros(0, dtype=dtype, order='F')
    for index in range(len(aList)):
        flatArray = np.concatenate((flatArray, aList[index].flatten().astype(dtype)))
    return flatArray


def MakeArrayListFromFlat(templateList, flatArray):
    aList = []
    currLocation = 0
    
    for templateElem in templateList:
        endLocation = currLocation+templateElem.size
        elem = np.reshape(flatArray[currLocation:endLocation], templateElem.shape)        
        currLocation = endLocation
        aList.append(elem)
        
    return aList
