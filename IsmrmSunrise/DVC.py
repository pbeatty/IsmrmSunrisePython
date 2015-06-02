__all__ = ["CreateFourierEncodingImages", "ComputeDvcKernels", "ComputeCcmFromKernels", "ComputeCcmDvc", "GenerateVcBlocks", "FitToAffinePhase", "FitToConstantPhase", "StitchVcBlocks"]

import numpy as np
from Display.Viewers import imshow2d
import IsmrmSunrise



def CreateFourierEncodingImages(imShape, kernelShape, kernelOversampling):
    """Creates Fourier incoding images for all kernel sample locations.
    
    Not the most efficient thing to do, but easy to understand.
    
    Parameters
    ----------
    imShape : length 2 vector
        Shape of image [Nx, Ny] e.g. [128,128]
    kernelShape : length 2 vector
        Shape of k-space kernel. e.g. [5,5]
    kernelOversampling : length 2 vector
        k-space oversampling ratio. e.g. [1.25, 1.25]

    Returns
    -------
    encodingImages : (Nx, Ny, Nkernelpoints)    
        Fourier encoding images for all of the kernel points.
        e.g. for a 5x5 kernel, there would be 25 kernel points
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    nx = imShape[0]
    ny = imShape[1]    
    numCoefficients = kernelShape[0] * kernelShape[1]

    x = np.arange(0, nx)
    y = np.arange(0, ny)
    xv, yv = np.meshgrid(x,y, indexing='ij')

    xkernelShape_2 = kernelShape[0] * 0.5
    ykernelShape_2 = kernelShape[1] * 0.5

    
    # form Fourier encoding images
    encodingImages = np.zeros((nx, ny, numCoefficients), dtype= np.complex)
    for kyi in range(kernelShape[1]):
        for kxi in range(kernelShape[0]):
            kx = (kxi - xkernelShape_2) / (kernelOversampling[0] * nx)
            ky = (kyi - ykernelShape_2) / (kernelOversampling[1] * ny)
            encodingImages[:,:, kxi + kernelShape[0]*kyi] = np.exp(2.0j * np.pi * (kx * xv + ky * yv))
    
    return encodingImages
    
    
def ComputeDvcKernels(channelImages, vcImage, kernelShape, kernelOversampling):
    """ Computes Dvc kernels
    
    Parameters
    ----------
    channelImages : (Nx, Ny, Nc) array
        Calibration channel images
    vcImage : (Nx, Ny) array
        Virtual coil image. Could also be an acquired calibration image from a 
        coil with sensitivity over the entire imaging region.
    kernelShape : length 2 vector
        shape of k-space kernel [kx, ky] (e.g. [5,5])
    kernelOversampling : length 2 vector
        k-space oversampling ratio. e.g. [1.25, 1.25]

    Returns
    -------
    kernels : (kx, ky, Nc) array
        k-space kernels. Channel images can be convolved with these kernels and combined in k-space
        
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
  
    """
    numChannels = channelImages.shape[2]    
    
    encodingImages = CreateFourierEncodingImages(vcImage.shape, kernelShape, kernelOversampling)    

    numVoxels = vcImage.size
    numCoefficients = kernelShape[0] * kernelShape[1]

    encodingImages = np.reshape(encodingImages, [numVoxels, numCoefficients], order='F')
    conjvcImage = np.conj(np.reshape(vcImage, [numVoxels, 1], order='F'))
    conjchannelImages = np.conj(np.reshape(channelImages, [numVoxels, numChannels], order='F'))
    Amatrix = np.mat(encodingImages * conjvcImage).H * np.mat(encodingImages * conjvcImage)
    bmatrix = np.mat(encodingImages * conjvcImage).H * np.mat(conjchannelImages)

    x = np.linalg.solve(Amatrix, bmatrix)        
            
    kernels = np.reshape(x.A, tuple(kernelShape) + (numChannels,), order='F')   
    return kernels

def ComputeCcmFromKernels(kernels, kernelOversampling, imShape):
    """ Compute Channel Combination Maps from k-space kernels. Intensity is normalized 
    to root sum-of-squares shading using NormalizeShadingToSoS.
    
    Parameters
    ----------
    kernels : (kx, ky, Nc) array
        k-space kernels.
    kernelOversampling : length 2 vector
        k-space oversampling ratio corresponding to kernels. e.g. [1.25, 1.25]
    imShape : length 2 vector
        shape of ccm image to produce (Nx, Ny)
    
    Returns
    -------
    ccm : (Nx, Ny, Nc) array
        Channel combination maps
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    encodingImages = CreateFourierEncodingImages(imShape, [kernels.shape[0], kernels.shape[1]], kernelOversampling)

    numCoefficients = encodingImages.shape[2]    
    numChannels = kernels.shape[2]
    nx = imShape[0]
    ny = imShape[1]

    coeff = np.mat(np.reshape(kernels, [numCoefficients, numChannels], order='F'))
    
    ccm = np.mat(np.reshape(encodingImages, [nx*ny, numCoefficients], order='F')) * coeff

    ccm = np.reshape(ccm.A, (nx, ny, numChannels), order='F')
    ccm = IsmrmSunrise.ChannelCombination.NormalizeShadingToSoS(ccm)[0]
    
    return ccm


def ComputeCcmDvc(im, kernelSize=None, kernelOversampling=None, ccmShape=None):
    """Compute Channel combination maps with DVC method
    
    Parameters
    ----------
    im : (calNx, calNy, Nc) array
        Calibration channel images
    kernelSize : length 2 vector
        Size of kernel in k-space, e.g. [5,5] or [7,7]
    kernelOversampling : length 2 vector
        oversampling ratio for kernel. default is [1.25, 1.25]
    ccmShape : length 2 vector
        ccm image shape (Nx, Ny). default is (calNx, calNy)
    
    Returns
    -------
    ccm : (Nx, Ny, Nc)
        Channel combination map    
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    if kernelOversampling is None:
        kernelOversampling = np.asarray([1.25, 1.25])
    if kernelSize is None:     
        kernelSize = np.asarray([5,5])

    imShape = np.asarray(im.shape[0:2])
    if ccmShape is None:
        ccmShape = imShape


    analysisBlockSize = imShape >> 2
    synthesisBlockSize = analysisBlockSize
    synthesisOverlap = imShape>>3

    eigBlocks = GenerateVcBlocks(im, analysisBlockSize, synthesisBlockSize, synthesisOverlap)

    vcImMag = IsmrmSunrise.ChannelCombination.ComputeRootSumOfSquaresChannelCombination(im)

    vcIm = np.exp(1j*StitchVcBlocks(eigBlocks, synthesisOverlap)) * vcImMag

    imshow2d([vcIm, vcImMag], windowTitle="vcIm", titles=["vcIm", "vcImMag"])

    kernels = ComputeDvcKernels(im, vcIm, kernelSize, kernelOversampling)

    ccmDvc = ComputeCcmFromKernels(kernels, kernelOversampling, ccmShape)
    return ccmDvc

def GenerateVcBlocks(im, analysisBlockSize, synthesisBlockSize, synthesisOverlap):
    """Creates overlapping channel combined blocks using the Walsh method.
    These can then be stitched together using StitchVcBlocks to derive the phase of the 
    virtual coil image.
    
    Parameters
    ----------
    im : (Nx, Ny, Nc) array
        Channel calibration images
    analysisBlockSize : length 2 vector
        Dominant eigenvector is computed over blocks of this size
    synthesisBlockSize : length 2 vector
        Dominant eigenvector is applied over blocks this size. Used to decide shift between blocks
    synthesisOverlap : length 2 vector
        Number of pixels overlap of synthesis blocks
            
    Returns
    -------
    eigBlocks: (blockSizex, blockSizey, numBlocksx, numBlocksy) 4-D array
        Set of overlapping blocks covering the imaging region, 
    
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    numChannels = im.shape[2]
    correlationLookup = IsmrmSunrise.ComputeFullCorrelationLookup(im)    
    matrixSet = IsmrmSunrise.ComputeMatrixSet(correlationLookup, analysisBlockSize, synthesisBlockSize, synthesisOverlap)
    nBlocks = matrixSet.shape[0:2]    
    matrixSet = matrixSet.reshape((np.prod(nBlocks),)+ matrixSet.shape[2:4], order='F')
    
    blockEigVecs = np.reshape(IsmrmSunrise.ComputeDominantEigenvectors(matrixSet, 5), nBlocks + matrixSet.shape[2:4], order='F')
    stepSize = synthesisBlockSize - synthesisOverlap

    vcBlocks = np.zeros(tuple(synthesisBlockSize)+nBlocks, dtype=np.complex, order='F')
    for yBlockIndex in range(nBlocks[1]):
        for xBlockIndex in range(nBlocks[0]):
            currLocation = np.array((xBlockIndex, yBlockIndex))
            start = currLocation * stepSize
            stop = start + synthesisBlockSize
            currEigVec = blockEigVecs[xBlockIndex, yBlockIndex,:].reshape((1,1,numChannels))
            currBlock = im[start[0]:stop[0],start[1]:stop[1],:]
            currVcBlock = np.sum(np.conj(currEigVec) * currBlock, axis=2)
            vcBlocks[:,:,xBlockIndex, yBlockIndex] = currVcBlock

    return vcBlocks    
    
def FitToAffinePhase(phaseDiff):
    """ Finds affine phase that matches to conj of input
    
    Note: This function doesn't try to do phase unwrapping and will fail with 
    inputs that have wrapped phase. It is a pedagogical example used to aid in 
    demonstrating the DVC approach, and should probably be replaced with something 
    more robust for use beyond learning about the method.
    
    Parameters
    ----------
    phaseDiff : (Nx, Ny)
        image with some phase to be removed. Typically input is taken as the 
        difference between two images as im1 * conj(im2)
    
    Returns
    -------
    phaseCorrection : (Nx, Ny)
        phasor (exp(1j*phase)) of affine phase result
    
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """

    anchorPhase = np.angle(phaseDiff.flatten()[np.argmax(np.abs(phaseDiff))])
    
    phaseDiff = phaseDiff * np.exp(-1j*anchorPhase)

    x = np.arange(0,phaseDiff.shape[0])
    y = np.arange(0, phaseDiff.shape[1])
    xv, yv = np.meshgrid(x, y, indexing='ij')
    weighting = np.abs(phaseDiff.flatten())
    Amatrix = np.mat(np.array((xv.flatten(), yv.flatten(), np.ones(phaseDiff.size))).T * weighting[:, np.newaxis])
    bmatrix = np.mat(np.angle(phaseDiff.flatten()) * weighting).T
    coeff = np.linalg.solve(Amatrix.H*Amatrix,Amatrix.H*bmatrix).A[:,0]
    phaseCorrection = np.exp(-1j * (xv*coeff[0] + yv * coeff[1] + coeff[2] + anchorPhase))

    #imshow2d([phaseDiff, np.conj(phaseCorrection), phaseDiff*phaseCorrection], block=True)    
    return phaseCorrection

def FitToConstantPhase(phaseDiff):
    """ Finds constant phase that matches to conj of input
    
    Parameters
    ----------
    phaseDiff : (Nx, Ny)
        image with some phase to be removed. Typically input is taken as the 
        difference between two images as im1 * conj(im2)
    
    Returns
    -------
    phaseCorrection : (Nx, Ny)
        phasor (exp(1j*phase)) of constant phase result
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """

    anchorPhase = np.angle(np.argmax(phaseDiff))
    phaseDiff = phaseDiff * np.exp(-1j*anchorPhase)
    avePhase = np.sum(np.angle(phaseDiff) * np.abs(phaseDiff)) / np.sum(np.abs(phaseDiff))    
    
    phaseCorrection = np.ones(phaseDiff.shape, dtype=np.complex, order='F') * np.exp(-1j*(anchorPhase+avePhase))    
    return phaseCorrection

    
def StitchVcBlocks(eigBlocks, overlap):
    """Combines blocks by trying to align the phase in overlapping regions
    
    Parameters
    ----------
    eigBlocks: (blockSizex, blockSizey, numBlocksx, numBlocksy) 4-D array
        Set of overlapping blocks covering the imaging region, 
        each block is already combined across channels (e.g. by the Walsh method)
    overlap: length 2 vector
        The amount of overlap of the blocks (in pixels)
    
    Returns
    -------
        imPhase : (Nx, Ny) array
            Resulting phase of image, after stitching
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """
    blockSize = np.asarray(eigBlocks.shape[0:2])
    nBlocks = np.asarray(eigBlocks.shape[2:4])
    imShape = nBlocks * blockSize - (nBlocks-1)*overlap
    im = np.zeros(imShape, dtype=np.complex, order='F')
    stepSize = blockSize-overlap


    yIndexOrder = range(nBlocks[1])[(nBlocks[1]>>1)::-1] + range(nBlocks[1])[((nBlocks[1]>>1)+1)::]
    xIndexOrder = range(nBlocks[0])[(nBlocks[0]>>1)::-1] + range(nBlocks[0])[((nBlocks[0]>>1)+1)::]

    firstBlock = True
    for iby in yIndexOrder:
        for ibx in xIndexOrder:
            currLocation = np.array((ibx, iby))
            start = currLocation * stepSize
            stop = start + blockSize
            if firstBlock :
                newPhase = eigBlocks[:,:,ibx, iby]
                phaseCorrection = FitToAffinePhase(newPhase)
                #imshow2d([newPhase, phaseCorrection], block=True)
                im[start[0]:stop[0], start[1]:stop[1]] = phaseCorrection*newPhase
                firstBlock = False
            else:
                existingPhase = im[start[0]:stop[0], start[1]:stop[1]]
                newPhase = eigBlocks[:,:,ibx, iby]
                phaseDiff = newPhase * np.conj(existingPhase)
                phaseCorrection = FitToAffinePhase(phaseDiff)
                #imshow2d([existingPhase, newPhase, phaseDiff, phaseCorrection, phaseCorrection*newPhase ])

                im[start[0]:stop[0], start[1]:stop[1]] = phaseCorrection * newPhase
                #imshow2d(im, windowTitle="block %d, %d"%(ibx, iby), block=True)
                
    return np.angle(im)

