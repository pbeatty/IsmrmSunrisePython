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
from Core import TransformDirection

def GenerateTestData(extent):
    testData = np.complex64(np.random.normal(size=extent) +1j * np.random.normal(size=extent))
    return testData



def cubicInterp(Din, newX, newY, newZ):
    import scipy.interpolate as interp
    
    xold = np.arange(0, Din.shape[0])
    yold = np.arange(0, Din.shape[1])
    zold = np.arange(0, Din.shape[1])
    
    xnew = np.linspace(0, Din.shape[0]-1, newX)
    ynew = np.linspace(0, Din.shape[1]-1, newY)
    znew = np.linspace(0, Din.shape[2]-1, newZ)
    
    f = interp.interp1d(xold, Din, kind='cubic', axis=0)
    D1 = f(xnew)
    
    f = interp.interp1d(yold, D1, kind='cubic', axis=1)
    D2 = f(ynew)

    f = interp.interp1d(zold, D2, kind='cubic', axis=2)
    D3 = f(znew)
    
    return D3

def ftInterp(Din, newX, newY, newZ):
    D = Din.copy().astype('complex64')
    oldX = D.shape[0]
    oldY = D.shape[1]
    oldZ = D.shape[2]
    
    RunPythonFTShift(D, D, 0, TransformDirection.FORWARD, 1.0/oldX, 0, -0.5 * oldX, 0.5*oldX )
    RunPythonFTShift(D, D, 1, TransformDirection.FORWARD, 1.0/oldY, 0, -0.5 * oldY, 0.5*oldY )
    RunPythonFTShift(D, D, 2, TransformDirection.FORWARD, 1.0/oldZ, 0, -0.5 * oldZ, 0.5*oldZ )
       
    nDx = np.zeros((newX, oldY, oldZ), dtype='complex64')
    nDy = np.zeros((newX, newY, oldZ), dtype='complex64')
    newD = np.zeros((newX, newY, newZ), dtype='complex64')

    RunPythonFTShift(nDx, D, 0, TransformDirection.BACKWARD, 1.0, 0, -0.5 * oldX, 0.5*newX )
    RunPythonFTShift(nDy, nDx, 1, TransformDirection.BACKWARD, 1.0, 0, -0.5 * oldY, 0.5*newY )
    RunPythonFTShift(newD, nDy, 2, TransformDirection.BACKWARD, 1.0, 0, -0.5 * oldZ, 0.5*newZ )
           
    return np.real(newD)

#
# currenlty only works for 2D array
#
def RunPythonFT(output, input, dim, transformDirection, scale, fftExtent, preShift, postShift):
    
    inputExtent = input.shape
    outputExtent = output.shape
        
    ftExtent = list(inputExtent)
    ftExtent[dim] = max(inputExtent[dim], outputExtent[dim], fftExtent)

    tempIn = np.zeros(ftExtent, np.complex64)
    tempIn[0:inputExtent[0], 0:inputExtent[1]] = input
    
    tempIn = np.roll(a=tempIn, shift=preShift, axis=dim) 
    
    if transformDirection == TransformDirection.FORWARD:
        tempOut = np.fft.fft(a=tempIn, axis=dim)
    else:
        tempOut = ftExtent[dim] * np.fft.ifft(a=tempIn, axis=dim)
    
    tempOut = np.roll(a=tempOut, shift=postShift, axis=dim)
    output[:,:] = scale * tempOut[0:outputExtent[0], 0:outputExtent[1]]




def RunPythonFTShift(output, input, dim, transformDirection, scale, fftExtent, preShift, postShift):
    inputExtent = input.shape
    outputExtent = output.shape
        
    ftExtent = list(inputExtent)
    ftExtent[dim] = max(inputExtent[dim], outputExtent[dim], fftExtent)

    inputIndices = []
    for currExtent in inputExtent:
        inputIndices.append(slice(0, currExtent))    
    #inputIndices = (slice(0,inputExtent[0]), slice(0,inputExtent[1]))
    
    outputIndices = []
    for currExtent in outputExtent:
        outputIndices.append(slice(0, currExtent))
    #outputIndices = (slice(0, outputExtent[0]), slice(0, outputExtent[1]))

    tileExtent = np.array(inputExtent)
    tileExtent[dim] = 1
    reshapeExtent = np.ones(input.ndim)
    reshapeExtent[dim] = inputExtent[dim]

    if transformDirection == TransformDirection.FORWARD:
        twiddleCoefficient = 1j * 2 * np.pi
    else:    
        twiddleCoefficient = -1j * 2 * np.pi
        
    X = np.linspace(0, inputExtent[dim]-1, inputExtent[dim])
    shiftPhasor = np.reshape(np.exp((twiddleCoefficient*X*postShift) / ftExtent[dim]), reshapeExtent)
    shiftMatrix = np.tile(shiftPhasor, tileExtent)    
        
    tempIn = np.zeros(ftExtent, np.complex64)        
    tempIn[inputIndices] = input * shiftMatrix

    reshapeExtent[dim] = outputExtent[dim]
    X = np.linspace(0, outputExtent[dim]-1, outputExtent[dim])
            
    if transformDirection == TransformDirection.FORWARD:
        tempOut = np.fft.fft(a=tempIn, axis=dim)
    else:
        tempOut = ftExtent[dim] * np.fft.ifft(a=tempIn, axis=dim)
        
    shiftScale = scale * np.exp((twiddleCoefficient*preShift*postShift)/ftExtent[dim])
    shiftPhasor = shiftScale * np.reshape(np.exp((-twiddleCoefficient*X*preShift) / ftExtent[dim]), reshapeExtent)

    shiftMatrix = np.tile(shiftPhasor, tileExtent)            
    output[...] = tempOut[outputIndices] * shiftMatrix

def ft1D(input, dimIndex=0):
    output = np.zeros(input.shape, np.complex64)

    RunPythonFTShift(output, input, dimIndex, TransformDirection.FORWARD, 1.0, 0, -input.shape[dimIndex]*0.5, output.shape[dimIndex]*0.5)
    return output

def ift1D(input, dimIndex=0):
    output = np.zeros(input.shape, np.complex64)

    RunPythonFTShift(output, input, dimIndex, TransformDirection.BACKWARD, 1.0/input.shape[dimIndex], 0, -input.shape[dimIndex]*0.5, output.shape[dimIndex]*0.5)
    return output

def ft2D(input):
    output = np.zeros(input.shape, np.complex64)

    RunPythonFTShift(output, input, 0, TransformDirection.FORWARD, 1.0, 0, -input.shape[0]*0.5, output.shape[0]*0.5)
    RunPythonFTShift(output, output, 1, TransformDirection.FORWARD, 1.0, 0, -input.shape[1]*0.5, output.shape[1]*0.5)
    return output
    
def ift2D(input):
    output = np.zeros(input.shape, np.complex64)

    RunPythonFTShift(output, input, 0, TransformDirection.BACKWARD, 1.0/input.shape[0], 0, -input.shape[0]*0.5, output.shape[0]*0.5)
    RunPythonFTShift(output, output, 1, TransformDirection.BACKWARD, 1.0/input.shape[1], 0, -input.shape[1]*0.5, output.shape[1]*0.5)
    return output
   
def ft3D(input):
    output = np.zeros(input.shape, np.complex64)

    RunPythonFTShift(output, input, 0, TransformDirection.FORWARD, 1.0, 0, -input.shape[0]*0.5, output.shape[0]*0.5)
    RunPythonFTShift(output, output, 1, TransformDirection.FORWARD, 1.0, 0, -input.shape[1]*0.5, output.shape[1]*0.5)
    RunPythonFTShift(output, output, 2, TransformDirection.FORWARD, 1.0, 0, -input.shape[2]*0.5, output.shape[2]*0.5)
    return output
    
def ift3D(input):
    output = np.zeros(input.shape, np.complex64)

    RunPythonFTShift(output, input, 0, TransformDirection.BACKWARD, 1.0/input.shape[0], 0, -input.shape[0]*0.5, output.shape[0]*0.5)
    RunPythonFTShift(output, output, 1, TransformDirection.BACKWARD, 1.0/input.shape[1], 0, -input.shape[1]*0.5, output.shape[1]*0.5)
    RunPythonFTShift(output, output, 2, TransformDirection.BACKWARD, 1.0/input.shape[2], 0, -input.shape[2]*0.5, output.shape[2]*0.5)
    return output 

#
# To test gridding
#
def dft(input, inputLocations, outputLocations):
    #nInput = input.shape(0)
    nOutput = outputLocations.shape[1]
    output = np.zeros(nOutput, dtype=np.complex128)
    
    for index in range(nOutput):
#        print index, nOutput
        encodeFn = np.exp(1j * 2 * np.pi * np.dot(outputLocations[:, index], inputLocations))
        output[index] = np.dot(encodeFn, input)
    return output
    
#
# To test inverse gridding
#
def idft(input, inputLocations, outputLocations):
    #nInput = input.shape(0)
    nOutput = outputLocations.shape[1]
    output = np.zeros(nOutput, dtype=np.complex128)
    
    for index in range(nOutput):
#        print index, nOutput
        encodeFn = np.exp(-1j * 2 * np.pi * np.dot(outputLocations[:, index], inputLocations))
        output[index] = np.dot(encodeFn, input)
    return output