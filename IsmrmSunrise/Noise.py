__all__ = ["GenerateCorrelatedNoise", 
           "EstimateCovarianceMatrix", 
           "EstimateCovariance", 
           "ComputeNoiseDecorrelationMatrixFromCovarianceMatrix",
           "ApplyNoiseDecorrelationMatrix",
           "ComputeNoiseAmplification"]

import numpy as np

def GenerateCorrelatedNoise(imShape, noiseCovarianceMatrix):
    """Generates noise that is correlated between channels

    Parameters
    ----------
    imShape : (Nx, Ny) array
        Matrix size
        
    noiseCovarianceMatrix : (Nc x Nc) array
        Noise covariance matrix for channels.  Make sure it is valid (positive definite)

    Returns
    -------
    noise : (Nx, Ny, Nc) array
        Matrix with correlated gaussian noise

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    nc = noiseCovarianceMatrix.shape[0]
    nx = imShape[0]
    ny = imShape[1]
    
    uncorrelatedNoise = np.mat(1.0/np.sqrt(2) * (np.random.randn(nc, nx*ny) + 1j * np.random.randn(nc, nx*ny)))
    correlationTransform = np.linalg.cholesky(np.mat(noiseCovarianceMatrix))
    correlatedNoise = correlationTransform * uncorrelatedNoise
    return np.reshape( np.asarray(correlatedNoise.T), (nx, ny, nc), order='F')


def EstimateCovarianceMatrix(noiseData):
    """Estimates a noise covariance matrix from noise samples
    
    Parameters
    ----------
    noiseData : (Nsamples, Nc) array
        Noise samples for a set of channels
        
    Returns
    -------
    noiseCoverianceMatrix : (Nc x Nx) array
        An estimate of the noise covariance matrix of the channels
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    noiseDataMatrix = np.mat(noiseData)    
    nSamples = noiseDataMatrix.shape[0]    
    noiseMatrix = noiseDataMatrix.T * noiseDataMatrix.conj() /  float(nSamples)    
    return noiseMatrix
    
def EstimateCovariance(channel1, channel2):
    """Estimate noise covariance between two channels from noise data from those channels
    
    Parameters
    ----------
    channel1 : array
        noise samples from one channel
    channel2 : array
        noise samples from another channel
        
    Returns
    -------
    covarianceEstimate : scalar
        covariance value estimate

    Notes
    -----        
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)        
    """
    assert channel1.shape == channel2.shape
        
    covEstimate = np.sum(channel1 * channel2.conj()) / float(channel1.size)
    return covEstimate

def ComputeNoiseDecorrelationMatrixFromCovarianceMatrix(noiseCovarianceMatrix):
    """Compute the noise decorrelation matrix for prewhitening from the noise covariance matrix

    Parameters
    ----------
    noiseCovarianceMatrix : (Nc, Nc) array
        noise covariance matrix
        
    Returns
    -------
    decorrelationMatrix : (Nc, Nc) array
        decorrelation matrix

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)        
    
    """
    
    decorrelationMatrix = np.conj(np.linalg.inv(np.linalg.cholesky(np.mat(noiseCovarianceMatrix))))
    return decorrelationMatrix
    
    
def ApplyNoiseDecorrelationMatrix(input, decorrelationMatrix, channelDim = None):
    """Applies noise decorrlation matrix to data (prewhitening)

    Parameters
    ----------
    input : (Nx, Ny, ... , Nc) array
        Input data, last dimension is coils
    decorrelationMatrix : (Nc, Nc) array
        Decorrelation matrix, e.g. as produced by ComputeNoiseDecorrelationMatrixFromCovarianceMatrix
 
   Returns
   -------
   output : (Nx, Ny, ..., Nc) array
       Output data, data with pre-whitened noise

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)        
    """    

    inputDims = input.ndim
    if channelDim is None:
        channelDim = inputDims-1    
    numChannels = input.shape[channelDim]

    assert decorrelationMatrix.ndim == 2, "decorrelationMatrix is not a 2 dimensional matrix"
    assert decorrelationMatrix.shape[0] == numChannels and decorrelationMatrix.shape[1] == numChannels, "decorrelationMatrix shape should be numChannels x numChannels"
    
    inputShape = input.shape
    numElements = input.size // numChannels
    
    inputMatrix = np.mat(np.reshape(input, [numElements, numChannels], order='F'))
    outputMatrix = np.mat(decorrelationMatrix) * inputMatrix.T    
    
    output = np.reshape(np.array(outputMatrix.T), inputShape, order='F')
    return output
          
            
def ComputeNoiseAmplification(unmixing, noiseMatrix=None):
    """Computes noise amplification from separate channel-by-channel images to a combined single channel image.

    Parameters
    ----------
    unmixing : (Nx, Ny, Nc) array
        unmixing images for accelerated case, channel combination maps for the unaccelerated case.
    noiseMatrix : (Nc, Nc) array
        noise covariance matrix

    Returns
    -------
    
    noiseAmplification : (Nx, Ny) array
        noise amplification map

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)        
    """
    
    channelDim = unmixing.ndim-1
    numChannels = unmixing.shape[channelDim]
    numElements = unmixing.size // numChannels
    imShape = unmixing.shape[0:channelDim]

    if noiseMatrix is None:
        noiseMatrix = np.eye(numChannels)
    noiseMatrix = np.mat(noiseMatrix)

    unmixingMat = np.mat(np.reshape(unmixing, [numElements, numChannels], order='F'))
    noiseAmplification = np.reshape(np.sqrt(np.abs(np.sum(np.multiply(unmixingMat * noiseMatrix, np.conj(unmixingMat)), 1).A)), imShape, order='F')
    
    return noiseAmplification
