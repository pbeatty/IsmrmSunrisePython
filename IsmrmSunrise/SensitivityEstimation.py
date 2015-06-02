__all__ = ["EstimateCsmMckenzie", "EstimateCsmWalsh", "ComputeDominantEigenvectors", "ComputeFullCorrelationLookup", "ComputeMatrixSet"]

import numpy as np

def EstimateCsmMckenzie(im):
    """Estimates relative coil sensitivity maps from a set of channel-by-channel 
    images, using method described in McKenzie et al. (Magn Reson Med 2002;47:529-538.)

    Parameters
    ----------
    im : (Nx, Ny, Nc) array
        Coil images
        
    Returns
    -------
    csm : (Nx, Ny, Nc) array
        Relative coil sensitivity maps

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """

    channelDim = im.ndim-1
    numChannels = im.shape[channelDim]
    numElements = im.size / numChannels

    imMatrix = np.reshape(im, [numElements, numChannels], order='F')
    scaleCorrection = np.sqrt(np.sum(np.abs(imMatrix)**2,1))

    nonzeroInd = np.nonzero(scaleCorrection)
    nonzeroScaleCorrection = scaleCorrection[nonzeroInd]
    
    csm = np.zeros(imMatrix.shape, dtype=np.complex)
    csm[nonzeroInd,:] = imMatrix[nonzeroInd,:] / nonzeroScaleCorrection[:,np.newaxis]
    csm = np.reshape(csm, im.shape, order='F')
    return csm

def EstimateCsmWalsh(im, smoothing=None):
    """Estimates relative coil sensitivity maps from a set of coil images
    using the eigenvector method described by Walsh et al. (Magn Reson Med
    2000;43:682-90.)

    Parameters
    ----------
    im : (Nx, Ny, Nc) array
        Coil images
    smoothing :  int
        Smoothing block size (defaults to 5)

    Returns
    -------
    csm : (Nx, Ny, Nc) array
        Relative coil sensitivity maps

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    if smoothing is None:
        smoothing = 5
    
    correlationLookup = ComputeFullCorrelationLookup(im)    
    
    synthesisBlockSize = np.asarray([1,1])
    analysisBlockSize = np.asarray([smoothing, smoothing])
    synthesisOverlap = np.array([0,0])    

    matrixSet = ComputeMatrixSet(correlationLookup, analysisBlockSize, synthesisBlockSize, synthesisOverlap)    
    
    matrixSet = matrixSet.reshape([matrixSet.shape[0] * matrixSet.shape[1], matrixSet.shape[2], matrixSet.shape[3]], order='F')
    
    csm = ComputeDominantEigenvectors(matrixSet, 5)
    csm = np.reshape(csm, im.shape, order='F')
    return csm

def ComputeMatrixSet(correlationLookup, analysisBlockSize, synthesisBlockSize, synthesisOverlap):
    """Computes a set of square correlation matrices between channels, based on input block sizes.
    Used as input to ComputeDominantEigenvectors
    
    Parameters
    ----------
    correlationLookup : (Nx, Ny, Nc, Nc) array
        Correlation between channels for each voxel. 
        Can be computed using ComputeFullCorrelationLookup
    analysisBlockSize : length 2 vector
        Dominant eigenvector is computed over blocks of this size
    synthesisBlockSize : length 2 vector
        Dominant eigenvector is applied over blocks this size. Used to decide shift between blocks
    synthesisOverlap : length 2 vector
        Number of pixels overlap of synthesis blocks
        
    Returns
    -------
    matrixSet : (numBlocksx, numBlocksy, Nc, Nc)
        Correlation matrices for all blocks
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)        
    """
    nx = correlationLookup.shape[0]
    ny = correlationLookup.shape[1]
    
    imShape = np.asarray(correlationLookup.shape[0:2])
    analysisBlockSize = np.asarray(analysisBlockSize)
    synthesisBlockSize = np.asarray(synthesisBlockSize)
    synthesisOverlap = np.asarray(synthesisOverlap)
    stepSize = synthesisBlockSize - synthesisOverlap
    outputShape = tuple((imShape - synthesisBlockSize)/ stepSize + 1) + correlationLookup.shape[2:4]
    output = np.zeros( outputShape, dtype=np.complex, order='F')
    
    
    minIndices = np.array([0,0])
    maxIndices = np.array([nx, ny])
    border = (analysisBlockSize-synthesisBlockSize)>>1
    
    for iy in range(output.shape[1]):
        for ix in range(output.shape[0]):
            currLocation = np.array((ix,iy))
            start = np.maximum(currLocation * stepSize - border, minIndices)
            stop = np.minimum(start + analysisBlockSize, maxIndices)
            
            output[ix, iy, :, :] = np.sum(correlationLookup[start[0]:stop[0], start[1]:stop[1], :, :], axis=(0,1))
            

    return output        


def ComputeFullCorrelationLookup(im):
    """Computes correlation between channels for all voxels.
    Correlation(ch1, ch2) = im(x,y,ch1) * conj(im(x,y,ch2))

    Parameters
    ----------
    im : (Nx, Ny, Nc) array
        channel-by-channel images
        
    Returns
    -------
    correlationLookup : (Nx, Ny, Nc, Nc) 4-D array
        correlation between channels for all voxels

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)        
    """
    import ChannelCombination
    channelDim = im.ndim-1
    numChannels = im.shape[channelDim]
    numElements = im.size / numChannels
    

    # normalize by root sum of squares magnitude & squish spatial dimensions to 1D
    voxels = ChannelCombination.NormalizeShadingToSoS(im)[0].reshape([numElements, numChannels], order='F')

    # compute sample correlation estimates at each pixel location
    correlationLookup = np.zeros([numElements, numChannels, numChannels], dtype=np.complex, order='F')
   
    for channelIndex1 in range(numChannels):
        correlationLookup[:,channelIndex1, channelIndex1] = np.abs(voxels[:,channelIndex1])**2        
        for channelIndex2 in range(channelIndex1):
            currCorrelation = voxels[:,channelIndex1] * np.conj(voxels[:,channelIndex2])
            correlationLookup[:, channelIndex1, channelIndex2] = currCorrelation
            correlationLookup[:, channelIndex2, channelIndex1] = np.conj(currCorrelation)

    return correlationLookup.reshape(im.shape + (numChannels,), order='F')

    
def ComputeDominantEigenvectors(matrixSet, numIterations = 2):
    """Uses the Power Method to compute a set of dominant eigenvectors in parallel

    Parameters
    ----------
    matrixSet : (numMatrices, matrixSize, matrixSize)
        A set (size numMatrices) of square matrices (matrixSize x matrixSize), 
        targets for computing the dominant eigenvector
    numIterations : int
        Number of iterations for the Power Method
    
    Returns
    -------
    dominantEigenVectors : (numMatrices, matrixSize)
        dominant eigenvector for each input matrix. 
        Returns all zeros for a zero valued input matrix
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    import ChannelCombination

    #
    # Step 1: strip out locations with no signal
    #
    matrixSize = matrixSet.shape[2]
    assert matrixSize == matrixSet.shape[1], "ComputeDominentEigenvectors requires a set of square matrices, input is of size: {}".format(str(matrixSet.shape)) 
    numMatrices = matrixSet.shape[0]

    nonzeroIndices = np.nonzero(np.max(np.max(matrixSet, axis=2), axis=1))
    matrixSet = matrixSet[nonzeroIndices, :, :]
    numNonzeroMatrices = matrixSet.shape[0]
    
    #
    # Step 2: Use Power Method to compute dominant eigenvector
    #
    currEigenvector = np.ones([numNonzeroMatrices, matrixSize], dtype = np.complex)
    
    for iterationIndex in range(numIterations):
        # multiply currEigenvector by matrices
        currEigenvector = np.squeeze(np.sum(np.conj(matrixSet) * currEigenvector[:,:, np.newaxis], axis=2))
        
        # scale. Exact scale isn't critical at this point, just want to limit amplification
        scale = np.max(np.abs(currEigenvector), 1)
        currEigenvector = currEigenvector / scale[:, np.newaxis]
        
    #
    # Step 3: Scale the eigenvector for SoS shading
    #         Set phase (which is arbitrary) so that first channel has no phase
    #
    normalizedEigenvector = ChannelCombination.NormalizeShadingToSoS(currEigenvector)[0]
    phaseCorrection = np.exp(-1.0j * np.angle(normalizedEigenvector[:,0]))
    normalizedEigenvector = normalizedEigenvector * phaseCorrection[:, np.newaxis]

    #
    # Step 4: put back signal locations to corresponding locations
    #    
    dominantEigenvector = np.zeros([numMatrices, matrixSize], dtype=np.complex)
    dominantEigenvector[nonzeroIndices,:] = normalizedEigenvector
    
    return dominantEigenvector