__all__ = ["ComputeChannelCombinationMaps", 
           "ComputeRootSumOfSquaresChannelCombination",
           "NormalizeShadingToSoS"]

import numpy as np

def ComputeChannelCombinationMaps(channelSensitivityMaps, noiseMatrix=None):
    """Computes noise-optimal channel combination maps from  coil sensitivity 
    maps and a noise covariance matrix.

    Parameters
    ----------

    channelSensitivityMaps : (Nx, Ny, Nc) array
        coil sensitivity maps
    noiseMatrix : (Nc, Nc) array
        noise covariance matrix

    Returns
    -------
    
    ccm : (Nx, Ny, Nc) array
        channel combination maps
        The ccm can be applied to channel-by-channel images as
        imComposite = sum(ccm * im_channel_by_channel, 2)

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    
    channelDim = channelSensitivityMaps.ndim - 1    
    numChannels = channelSensitivityMaps.shape[channelDim]
    
    numElements = channelSensitivityMaps.size // numChannels    
    
    if noiseMatrix is None:
        noiseMatrix = np.eye(numChannels)
    

    csmMatrix = np.mat(np.reshape(channelSensitivityMaps, [numElements, numChannels], order='F'))

    relativeCcmMatrix = np.conj(csmMatrix) * np.linalg.pinv(noiseMatrix)

    scaleCorrection = np.array(np.abs(np.sum(np.multiply(relativeCcmMatrix, csmMatrix), 1)))

    nonzeroInd = np.nonzero(scaleCorrection)
    nonzeroScaleCorrection = scaleCorrection[nonzeroInd]

    ccm = np.zeros(csmMatrix.shape, dtype=complex)
    
    ccm[nonzeroInd, :] = np.array(relativeCcmMatrix[nonzeroInd,:]) / nonzeroScaleCorrection[:, np.newaxis]


    ccm = np.reshape(ccm, channelSensitivityMaps.shape, order='F');
    return ccm
    

def ComputeRootSumOfSquaresChannelCombination(x, dimIndex=None):
    """Computes root-sum-of-squares along a single dimension.

    Parameters
    ----------
    x : array
        multi-dimensional array of samples
    dimIndex : scalar
        dimension of reduction; defaults to last dimension

    Returns
    -------
    
    y : array
        root sum of squares result
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """

    if dimIndex is None:
        dimIndex = x.ndim-1
    y = np.sqrt(np.sum(np.real(x)**2 + np.imag(x)**2, dimIndex)).squeeze()
    
    return y


def NormalizeShadingToSoS(imIn):
    """Applies correction to csm or ccm images so that the shading profile is
    the same as a square root sum-of-squares channel combination.  This
    allows normalization of the shading profile between different
    reconstruction methods.

    Parameters
    ----------
    imIn : (Nx, Ny, Nc) array
        input ccm or csm images

    Returns
    -------
    imOut : (Nx, Ny, Nc) array
        shading normalized output ccm or csm

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    
    channelDim = imIn.ndim-1
    numChannels = imIn.shape[channelDim]
    numElements = imIn.size // numChannels
    imShape = list(imIn.shape[0:channelDim])
    imShape.append(1)
    
    imInMatrix = np.reshape(imIn, [numElements, numChannels], order='F')
    
    shadingCorrection = np.sqrt(np.sum(np.abs(imInMatrix)**2, 1))
    nonzeroInd = np.nonzero(shadingCorrection)

    correctionImage = np.zeros(shadingCorrection.shape)
    correctionImage[nonzeroInd] = 1.0 / shadingCorrection[nonzeroInd]
    correctionImage = np.reshape(correctionImage, imShape, order='F')

    imOut = imIn * correctionImage
    correctionImage = correctionImage.squeeze()
    
    return imOut, correctionImage