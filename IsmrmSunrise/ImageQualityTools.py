__all__ = ["ComputeGmap", "ComputeAliasingEnergyMap"]

import numpy as np

def ComputeGmap(unmixing, ccm, accFactor, noiseMatrix=None):
    """Computes g-factor map (relative noise enhancement between unaccelerated 
    and accelerated case normalized by scan time.

    N.B. This function assumes that unmixing operates on aliased images
    formed from data that is scaled the same as the fully sampled case, but
    with (R-1)/R of the data set to zero.  As such, std dev. noise of fully
    sampled channel-by-channel images = sqrt(R) * std dev. noise of
    channel-by-channel aliased images.  This is accounted for by dividing by
    R in this function instead of sqrt(R).  When the unmixing and ccm are
    applied to the accelerated and fully sampled data, the final images
    should be scaled identically.

    Parameters
    ----------
    unmixing : (Nx, Ny, Nc) array
        unmixing images for accelerated case
    ccm : (Nx, Ny, Nc) array
        channel combination maps
    accFactor : int
        acceleration factor corresponding to unmixing

    noiseMatrix : (Nc, Nc) array
        noise covariance matrix

    Returns
    -------
    gmap : (Nx, Ny)
        g-factor map
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    from . import Noise
    
    channelDim = unmixing.ndim-1
    numChannels = unmixing.shape[channelDim]
    numElements = unmixing.size // numChannels
    imShape = unmixing.shape[0:channelDim]
  

    unmixingMat = np.mat(np.reshape(unmixing, [numElements, numChannels], order='F'))
    ccmMat = np.mat(np.reshape(ccm, [numElements, numChannels], order='F'))

    acceleratedNoiseAmplification = Noise.ComputeNoiseAmplification(unmixingMat, noiseMatrix)
    unacceleratedNoiseAmplification = Noise.ComputeNoiseAmplification(ccmMat, noiseMatrix)
    
    nonzeroInd = np.nonzero(unacceleratedNoiseAmplification)[0]

    gmap = np.zeros(numElements)

    gmap[nonzeroInd] = acceleratedNoiseAmplification[nonzeroInd] / (unacceleratedNoiseAmplification[nonzeroInd]* accFactor)
    
    gmap = np.reshape(gmap, imShape)

    return gmap

    

def ComputeAliasingEnergyMap(pixelMask, trueCsm, unmixing, accFactor):
    """Computes the square root of an "aliasing energy map" 
    
    Parameters
    ----------
    pixelMask : (Nx, Ny) array
        1 = pixel that might have signal
        0 = pixel that won't have signal
    trueCsm : (Nx, Ny, Nc) array
        ground truth coil sensitivity maps
    unmixing : (Nx, Ny, Nc) array
        unmix images under evaluation
    accFactor : int
        acceleration factor corresponding to unmixing

    Returns
    -------
    
    aem : (Nx, Ny) array
        square root of aliasing energy map

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """

    imShape = pixelMask.shape

    maskedCsm = trueCsm * pixelMask[:,:,np.newaxis]
    
    aem = np.zeros(imShape)
    
    # Use 'partition' to refer to a portion of the image corresponding to the reduced FOV due to undersampling
    partitionExtent = imShape[1] // accFactor
    firstPartitionIndices = np.arange(0, partitionExtent)

    for aIndex in range(accFactor):
        partitionIndices = firstPartitionIndices + aIndex * partitionExtent                
        imAlias = np.tile(maskedCsm[:, partitionIndices,:], [1, accFactor, 1])

        imHat = np.abs(np.sum(imAlias * unmixing, 2)) / accFactor
        imHat[:,partitionIndices] = 0
        aem = aem + imHat**2

    aem = np.sqrt(aem)
    return aem
