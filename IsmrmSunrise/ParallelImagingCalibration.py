__all__ = ["ComputeJerModelDriven", "ComputeJerDataDriven", "ComputeJerDataDrivenReference", "ComputeSenseUnmixing", "ComputeJerUnmixing", "ComputeUnmixingImagesFromKspaceKernels"]

import numpy as np
import time

def ComputeJerModelDriven(csm, kernelShape):
    """Computes a lookup table of joint encoding relationships (JER) using the
    model driven formulation given in Beatty PJ. Reconstruction methods for
    fast magnetic resonance imaging. PhD thesis, Stanford University, 2006.
    JERs were previous called "correlation values"; the name has been changed 
    to avoid confusion with correlation coefficients, used to relate
    two random variables.

    Parameters
    ----------
    
    csm : (Nx, Ny, Nc) array
        coil sensitivity map (can also be weighted coil sensitivity map)
    kernelShape : length 2 vector
        kernel shape on a fully sampled grid, [kx_extent, ky_extent]
        e.g. for acceleration=2, ky_extent=7 would use 4 source points along ky; 
        for acceleration=4, only 2 source points would be used.

    Returns
    -------
    jerLookup : (kx,ky,Nc, kx, ky, Nc) 6-D array
        lookup table of all joint encoding relations between kernel sample locations.
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    import Transforms
    
    channelDim = csm.ndim-1
    numChannels = csm.shape[channelDim]

    jerLookup = np.zeros(kernelShape + kernelShape + [numChannels, numChannels], dtype=np.complex)

    nx = csm.shape[0]
    ny = csm.shape[1]
    nx_2 = np.right_shift(nx, 1)
    ny_2 = np.right_shift(ny, 1)

    for ic2 in range(numChannels):
        for ic1 in range(numChannels):
            lookup = Transforms.TransformImageToKspace(np.conj(csm[:,:,ic1]) * csm[:,:,ic2], scale = [1.0, 1.0])
            for ikyb in range(kernelShape[1]):
                for ikxb in range(kernelShape[0]):
                    for ikya in range(kernelShape[1]):
                        for ikxa in range(kernelShape[0]):
                            jerLookup[ikxa, ikya, ikxb, ikyb, ic1, ic2] = lookup[nx_2 + ikxb - ikxa, ny_2 + ikyb-ikya]
    return jerLookup
    
    
def ComputeJerDataDrivenReference(calData, kernelShape):
    """Computes a lookup table of joint encoding relationships (JER) using the
    data driven formulation given in Beatty et al. Proc. ISMRM 2007, p1749.
    JERs were previous called "correlation values"; the name has been changed 
    to avoid confusion with correlation coefficients, used to relate
    two random variables.

    This function computes each JER independently.  This is not very
    efficient, but it is useful as a reference for testing accelerated computation
    approaches.

    Parameters
    ----------
    
    calData : (kx,ky,Nc)
        Calibration data (k-space)
    kernelShape : length 2 vector
        kernel shape on a fully sampled grid [kx_extent, ky_extent]
        e.g. for acceleration=2, ky_extent=7 would use 4 source points along ky; 
        for acceleration=4, only 2 source points would be used.

    Returns
    -------
    jerLookup : (kx,ky,Nc, kx, ky, Nc) 6-D array
        lookup table of all joint encoding relations between kernel sample locations.
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """

    nc = calData.shape[2]
    wx = kernelShape[0]
    wy = kernelShape[1]

    nfitx = calData.shape[0] - wx
    nfity = calData.shape[1] - wy
    jerLookup = np.zeros(kernelShape + kernelShape + [nc, nc], dtype=np.complex)

    xInd = np.arange(0, nfitx)
    yInd = np.arange(0, nfity)
    cInd = np.arange(0,1)

    for icb in range(nc):
        for ica in range(nc):
            for kyb in range(wy):
                for kxb in range(wx):
                    for kya in range(wy):
                        for kxa in range(wx):
                            jerLookup[kxa, kya, kxb, kyb, ica, icb] = np.sum(np.conj(calData[np.ix_(kxa+xInd, kya+yInd, ica+cInd)]) * (calData[np.ix_(kxb+xInd, kyb+yInd, icb+cInd)]))
    return jerLookup


def ComputeJerDataDriven(calData, kernelShape):
    """Computes a lookup table of joint encoding relationships (JER) using the
    data driven formulation given in Beatty et al. Proc. ISMRM 2007, p1749.
    JERs were previous called "correlation values"; the name has been changed 
    to avoid confusion with correlation coefficients, used to relate
    two random variables.

    This function computes JERs jointly when there is a common delta
    between the two encoding locations.  This gives some computational
    reduction.  This function does not take advantage of the symmetry that
    JER(a,b) = JER(b,a)*.  Also, since it is written in Python with for
    loops, it's runtime is not fast; it's purpose is mainly pedagogical.

    Parameters
    ----------    
    calData : (kx,ky,Nc)
        Calibration data (k-space)
    kernelShape : length 2 vector
        kernel shape on a fully sampled grid [kx, ky]
        e.g. for acceleration=2, ky_extent=7 would use 4 source points along ky; 
        for acceleration=4, only 2 source points would be used.

    Returns
    -------
    jerLookup : (kx,ky,Nc, kx, ky, Nc) 6-D array
        lookup table of all joint encoding relations between kernel sample locations.
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    assert calData.ndim == 3, 'cal_data must have 3 dimensions'
    #assert kernelShape.shape[0] == 2, 'kernel_shape must be a length 2 vector'

    nc = calData.shape[2]
    calShape = calData.shape[0:2]
    
    jerLookup = np.zeros(kernelShape + kernelShape + [nc, nc], dtype=np.complex)


    for dky in range(-(kernelShape[1]-1), kernelShape[1]):
        for dkx in range(-(kernelShape[0]-1), kernelShape[0]):
            dk = np.array([dkx, dky])
            partialSums = ComputePartialSums(calData, kernelShape, dk)
              
            nsums = kernelShape - np.abs(dk)
            sumSize = np.minimum(np.array(nsums), np.array(calShape) - np.array(kernelShape)+1)
            kx_a_min = max(0, -dkx)
            ky_a_min = max(0, -dky)
                
            for iky in range(nsums[1]):
                for ikx in range(nsums[0]):
                    kxa_index = kx_a_min + ikx
                    kya_index = ky_a_min + iky
                    currPartialSums = partialSums[(ikx):(sumSize[0]+ikx), (iky):(sumSize[1]+iky), :, :]
                    jerLookup[kxa_index, kya_index, kxa_index + dkx, kya_index + dky, :, :] = np.sum(np.sum(currPartialSums,1),0)

    return jerLookup          
            
   
def ComputePartialSums(calData, kernelShape, delta):
    """Computes partial sums as intermediate step used by ComputeJerDataDriven
    
    Parameters
    ----------
    calData : (kx, ky, Nc) array
        Calibration data (k-space)    
    kernelShape : length 2 vector
        kernel shape on a fully sampled grid [kx, ky]    
    delta : length 2 vector
        distance along kx and ky between two sample locations

    Returns
    -------
    partialSums : (nGroupsx, nGroupsy, Nc, Nc)
        partial sums for the given delta and kernel shape. 
        Different deltas have different numbers of partial sums.
        nGroups = minimum(2*kernelShape - abs(delta)-1, calShape-abs(delta)

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    ndims = calData.ndim-1
    calShape = calData.shape[0:ndims]
    nData = calShape - abs(delta);
    nGroups = np.minimum(2*(kernelShape - np.abs(delta))-1, calShape-np.abs(delta))
    nGroups_2 = np.right_shift(nGroups,1)
    
    
    sumMatrix = []
    
    for dimIndex in range(ndims):
        matrixEdges = np.mat(np.eye(nGroups[dimIndex]))
        matrixMiddle = np.tile(matrixEdges[:,nGroups_2[dimIndex]], [1, nData[dimIndex]-nGroups[dimIndex]])
        matrixFirst = matrixEdges[:, 0:nGroups_2[dimIndex]]
        matrixLast = matrixEdges[:, nGroups_2[dimIndex]:nGroups[dimIndex]]
        sumMatrix.append( np.mat(np.concatenate( (matrixFirst, matrixMiddle, matrixLast), axis=1 )))
    
    kx_a_min = max(0, -delta[0])
    ky_a_min = max(0, -delta[1])
    
    nc = calData.shape[calData.ndim-1]
    partialSums = np.zeros([nGroups[0], nGroups[1], nc, nc], dtype=np.complex)
    
    xRange_a = kx_a_min + np.arange(0, nData[0])    
    yRange_a = ky_a_min + np.arange(0, nData[1])

    xRange_b = xRange_a + delta[0]
    yRange_b = yRange_a + delta[1]    
    
    cRange = np.arange(0,1)
    for icb in range(nc):
        subData_b = np.mat(calData[np.ix_(xRange_b, yRange_b, cRange+icb)])
        for ica in range(nc):
            subData_a = np.mat(calData[np.ix_(xRange_a, yRange_a, cRange+ica)])
            subDataMult = np.multiply(np.conj(subData_a), (subData_b))
            partialSums[:,:,ica, icb] = sumMatrix[0] * subDataMult * sumMatrix[1].T
    return partialSums
    
def ComputeSenseUnmixing(accFactor, csm, noiseMatrix=None, regularizationFactor=0.001):
    """Calculates the unmixing coefficients for a 2D image

    Parameters
    ----------
    accFactor : scalar
        Acceleration factor, e.g. 2
    csm  : (Nx, Ny, Nc)
        Coil sensitivity map 
    noiseMatrix : (Nc, Nc)
        noise covariance matrix
    regularizationFactor : scaler
        adds Tychonov regularization.
        0 = no regularization
        0.001 = default
        set higher for more aggressive
        regularization.

    Returns
    -------
    unmix : (Nx, Ny, Nc) array
        Image unmixing coefficients for a single x location 
    gmap : (Nx, Ny) array
        Noise enhancement map 

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    assert csm.ndim == 3, "coil sensitivity map must have 3 dimensions"
    numChannels = csm.shape[csm.ndim-1]

    if noiseMatrix is None:
        noiseMatrix = np.eye(numChannels)        

    unmix = np.zeros(csm.shape, dtype=np.complex)


    noiseMatrixInv = np.linalg.pinv(noiseMatrix)

    tic = time.time()
    for xIndex in range(csm.shape[0]): 
        unmix[xIndex,:,:] = ComputeSenseUnmixing1d(accFactor, np.squeeze(csm[xIndex,:,:]), noiseMatrixInv, regularizationFactor) 
    print 'for loop time %f' %(time.time()-tic)

    return unmix

def ComputeSenseUnmixing1d(accFactor, csm1d, noiseMatrixInv, regularizationFactor=0.001):
    """ Computes SENSE unmixing coefficients for a single x location
    
    Parameters
    ----------
    accFactor : scalar
        Acceleration factor, e.g. 2
    csm  : (Ny, Nc) array
        Coil sensitivity map at a single x location
    noiseMatrixInv : (Nc, Nc)
        inverse of noise covariance matrix for channel array
    regularizationFactor : scaler
        adds Tychonov regularization.
        0 = no regularization
        0.001 = default
        set higher for more aggressive
        regularization.

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    numy = csm1d.shape[0]
    #numChannels = csm1d.shape[1]

    assert numy % accFactor == 0, "ny must be a multiple of acc_factor"

    unmix1d = np.zeros(csm1d.shape, dtype=np.complex)

    numBlocks = numy/accFactor
    for index in range(numBlocks):
        A = np.mat(csm1d[index::numBlocks,:]).T
        if np.max(np.abs(A)) > 0:  
            #unmix1d(index:n_blocks:ny, :) = pinv(A);
            AHA = A.H * np.mat(noiseMatrixInv) * A
            reducedEye = np.diag(np.abs(np.diag(AHA))>0).astype(np.int)
            numAlias = np.sum(reducedEye)
            scaledRegFactor = regularizationFactor * np.trace(AHA)/numAlias
        
            unmix1d[index::numBlocks, :] = np.linalg.pinv(AHA + reducedEye * scaledRegFactor) * A.H * noiseMatrixInv
    
    return unmix1d

def ComputeJerUnmixing(jerLookup, accFactor, ccm, regularizationScale=0.0, verbose=False): 
    """Calculates channel-by-channel local k-space unaliasing kernels based on
    the provided joint-encoding relations and acceleration factor.

    Transforms these kernels to image space and merges them with the
    provided channel combination maps to create unmixing images.

    Parameters
    ----------
    jerLookup : (kx,ky,Nc, kx, ky, Nc)
        Lookup table of joint encoding relations. 
        Kernel extent taken from jer size.
    accFactor : scalar
        Acceleration factor, e.g. 2
    ccm : (Nx, Ny,Nc)
        Channel combination maps
    regularizationScale : scalar
        Controls aggressiveness of Tychonov regularization during 
        calculation of unaliasing kernels.
        0 = no regularization;
        0.001 = default;
        higher for more aggressive regularization.
    verbose : bool
        Set true for verbose output

    Returns
    -------
    unmix : (Nx, Ny, Nc) array
        Image unmixing coefficients

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """

    #
    # Compute unaliasing kernels
    #
    
    if verbose:
        print 'Calculating unaliasing kernels...'

    kernelShape = [jerLookup.shape[0], jerLookup.shape[1] ]
    targetLocation = np.right_shift(kernelShape, 1)
    numChannels = ccm.shape[2]
    kernel = np.zeros( (kernelShape + [numChannels, numChannels]), dtype = np.complex )

    for ic in range(numChannels):
        kernel[targetLocation[0], targetLocation[1], ic, ic] = 1

    for s in range(accFactor-1):
        kernelMask = np.zeros(kernelShape)
        kernelMask[:,s::accFactor] = 1
        k = ComputeKspaceUnaliasingCoefficients(jerLookup, kernelMask, regularizationScale)
        kernel = kernel + k

    #
    # Form unmixing images from channel combination maps and kernels
    #

    if verbose:
        print 'Merging unaliasing and channel combination images...'


    unmix = ComputeUnmixingImagesFromKspaceKernels(kernel, ccm)

    if verbose:
        print 'done.'

    return unmix

def ComputeUnmixingImagesFromKspaceKernels(kernel, ccm):
    """Compute unmixing images from k-space unaliasing kernels and channel combination maps.

    Parameters
    ----------
    kernels : (kx, ky, NcSource, NcTarget) 4-D array
        k-space unaliasing kernels (for uniform undersampling pattern)
    ccm : (Nx, Ny, NcTarget) 3-D array
        channel combination maps

    Returns
    -------
    unmix : (Nx, Ny, NcSource) 3-D array
        Image unmixing coefficients

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    import Transforms
    nx = ccm.shape[0]
    ny = ccm.shape[1]
    numSourceChannels = kernel.shape[2]
    numTargetChannels = kernel.shape[3]
    assert numTargetChannels == ccm.shape[2], 'numTargetChannels in kernels does not match ccm'

    unmix = np.zeros([nx, ny, numSourceChannels], dtype=np.complex)

    imKernel = Transforms.TransformKernelToImageSpace(kernel, [nx, ny])

    for cIndex in range(numSourceChannels):
        unmix[:,:,cIndex] = np.sum(np.squeeze(imKernel[:,:,cIndex,:]) * ccm, 2)

    return unmix

def ComputeKspaceUnaliasingCoefficients(jerLookup, kernelMask, regularizationScale=0.0):
    """Compute kspace unaliasing coefficients from joint encoding relations.

    Parameters
    ----------
    jerLookup : (kx,ky, Nc, kx, ky, Nc)
        joint encoding relations lookup table
    kernel_mask : (kx,ky)
        e.g [1 1 1; 0 0 0; 1 1 1] for a 3x3 kernel with an acceleration factor of 2.
    regularizationScale : scalar
        amount of Tychonov regularization to apply.
        0 (default) = no regularization.
        0.001 moderate regularization
        higher value for more regularization.

    Returns
    -------
    kernel : (kx, ky, NcSource, NcTarget) 4-D array
        k-space unaliasing kernels (for uniform undersampling pattern)
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    assert regularizationScale >= 0, 'regularization_scale must be positive'

    kyOffsets, kxOffsets = np.nonzero(kernelMask.T==1)
    #[kx_offsets, ky_offsets] = ind2sub(size(kernel_mask), find(kernel_mask == 1));

    numSource = kxOffsets.shape[0]
    numChannel = jerLookup.shape[4]

    Rss = np.zeros((numSource, numChannel, numSource, numChannel), dtype=np.complex)
    Rst = np.zeros((numSource, numChannel, numChannel), dtype=np.complex)


    for is2 in range(numSource):
        for is1 in range(numSource):
            Rss[is1, :, is2, :] = jerLookup[kxOffsets[is1],
                                            kyOffsets[is1], 
                                            kxOffsets[is2],
                                            kyOffsets[is2],
                                            :, :]

    kxTarget = np.right_shift(kernelMask.shape[0], 1)
    kyTarget = np.right_shift(kernelMask.shape[1], 1)

    for is1 in range(numSource):
        Rst[is1, :, :] = jerLookup[kxOffsets[is1],
                                    kyOffsets[is1],
                                    kxTarget,
                                    kyTarget,
                                    :, :]
            
    numBasis = numSource * numChannel
    Rss = np.reshape(Rss, [numBasis, numBasis], order='F')
    Rst = np.reshape(Rst, [numBasis, numChannel], order='F')

    weights = np.linalg.solve((Rss + np.eye(numBasis) * (regularizationScale * np.trace(Rss) / numBasis) ), Rst)
    weights = np.reshape(weights, [numSource, numChannel, numChannel], order='F')

    kernel = np.zeros([kernelMask.shape[0], kernelMask.shape[1], numChannel, numChannel], dtype=np.complex)
    kernel[kxOffsets, kyOffsets, :, :] = weights
    
    return kernel