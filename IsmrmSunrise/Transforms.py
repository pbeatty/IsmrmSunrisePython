__all__ = ["TransformImageToKspace", "TransformKspaceToImage", "TransformKernelToImageSpace", "FlipDim", "MultiDimensionalFourierTransform"]

import numpy as np
import PythonFT

def TransformKernelToImageSpace(kernel, outShape):
    """Transforms a k-space convolution kernel to image space (for multiplication)

    Parameters
    ----------
    kernel : (kx, ky, ..., sourceNc, targetNc) array
        k-space convolution kernel
    outShape : (Nx, Ny) array
        Image size. e.g. (128,128)
        
    Returns
    -------
    imKernel : (Nx, Ny, Nc) array
        Image multiplication kernel    

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    numSpatialDimensions = kernel.ndim - 2 
    numSourceChannels = kernel.shape[numSpatialDimensions]
    numTargetChannels = kernel.shape[numSpatialDimensions+1]

    #Flip kernel since we will be FFTing to image space for pixel wise mult
    for d in range(numSpatialDimensions):
        kernel = FlipDim(kernel,d)

    outDimensions = outShape + [numSourceChannels, numTargetChannels]
    imKernel = TransformKspaceToImage(kernel, range(numSpatialDimensions), outDimensions, scale=[1.0, 1.0])
    return imKernel

def FlipDim(a, dim=0):
    """Flips values of an array along a given dimension
    
    Parameters
    ----------
    a : array
        input array (target of flip)
    dim : scalar
        dimension index for shift
                
    Returns
    -------
    aPrime : array
        flipped version of a    

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    a = np.asanyarray(a)
    idx = [slice(None)]*len(a.shape)
    idx[dim] = slice(None, None, -1)
    return a[tuple(idx)]

def TransformImageToKspace(im, dim=None, kShape=None, scale=None, fftExtent=None, preShift=None, postShift=None):
    """Fourier transform from image space to k-space space along a given or all 
    dimensions

    Parameters
    ----------
    img : (Nx, Ny, ...) array
        image space data
    dim : index vector
        Vector with dimensions to transform
    kShape : vector
        Set shape of output k-space matrix
    scale : vector
        scale k-space, one value gets applied with the transform in each direction
    fftExtent : vector
        extent of Fast Fourier Transform applied per dimension
    preShift : vector
        shift to apply before Fast Fourier Transform. non-integer component applied as linear phase after FFT
    postShift: vector
        shift to apply after Fast Fourier Transform. non-integer component applied ast linear phase before FFT

    Returns
    -------
    kData : (kx, ky, ...)
        Data in k-space (along transformed dimensions)

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """

    result = MultiDimensionalFourierTransform(im, dim, kShape, scale, fftExtent, preShift, postShift, PythonFT.TransformDirection.FORWARD)

    return result

def TransformKspaceToImage(kspace, dim=None, imShape=None, scale=None, fftExtent=None, preShift=None, postShift=None):
    """Fourier transform from image space to k-space space along a given or all 
    dimensions

    Parameters
    ----------
    kspace : (kx, ky,...) array
        kspace data
    dim : vector        
        Vector with dimension indices to transform
    imShape : vector
        Set shape of output image matrix
    scale : vector
        scale k-space, one value gets applied with the transform in each direction
    fftExtent : vector
        extent of Fast Fourier Transform applied per dimension
    preShift : vector
        shift to apply before Fast Fourier Transform. non-integer component applied as linear phase after FFT
    postShift: vector
        shift to apply after Fast Fourier Transform. non-integer component applied ast linear phase before FFT
        
    Returns
    -------
    im : (Nx, Ny, ...) array
        image matrix (along transformed dimensions)

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """

    result = MultiDimensionalFourierTransform(kspace, dim, imShape, scale, fftExtent, preShift, postShift, PythonFT.TransformDirection.BACKWARD)
    return result


def MultiDimensionalFourierTransform(inputMatrix, dim=None, outputShape=None, scale=None, fftExtent=None, preShift=None, postShift=None, direction = PythonFT.TransformDirection.BACKWARD):
    """Computes a multi-dimensional Fourier Transform

    Parameters
    ----------
    inputMatrix : array
        data to be transformed
    dim : vector
        indices of dimensions to apply transform
    outputShape : vector
        shape of output array. values ignored along dimensions not being transformed
    scale : vector
        multiplicative scale for each dimensions transform. values ignored along dimensions not being transformed
    fftExtent : vector
        length of Fast Fourier Transform (FFT) to apply
    preShift : vector        
        shift to apply before Fast Fourier Transform. non-integer component applied as linear phase after FFT
    postShift: vector
        shift to apply after Fast Fourier Transform. non-integer component applied ast linear phase before FFT

    Returns
    -------
    outputMatrix : array
        data after Fourier Transform
    
    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)

    """
    if dim is None:
        dim = range(inputMatrix.ndim)

    if outputShape is None:
        outputShape = inputMatrix.shape
    
    if scale is None:
        scale = 1.0 / np.sqrt(inputMatrix.shape)

    if fftExtent is None:
        fftExtent = np.zeros(inputMatrix.ndim)
    
    if preShift is None:
        preShift = -np.floor(np.array(inputMatrix.shape) * 0.5) 

    if postShift is None:
        postShift = np.floor(np.array(outputShape) * 0.5)

    input = inputMatrix.astype(np.complex64)
    for dimIndex in dim:
        currOutputShape = np.array(input.shape)
        currOutputShape[dimIndex] = outputShape[dimIndex]
        output = np.zeros(currOutputShape, dtype = np.complex64)
        PythonFT.RunPythonFTShift(output, input, dimIndex, direction, scale[dimIndex], fftExtent[dimIndex], preShift[dimIndex], postShift[dimIndex])
        input = output

    return input


