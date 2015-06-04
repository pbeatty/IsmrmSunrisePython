__all__=["GenerateAcceleratedSamplingPattern", "ExtractCalData"]

import numpy as np

def GenerateAcceleratedSamplingPattern(dataShape, acc, ref=0, sshift=0):
    """Returns a binary image of an accelerated sampling pattern in k-space.

    Parameters
    ----------
    dataShape : tuple
        matrix shape of fully sampled k-space data (kx, ky)
    acc : int
        Acceleration factor
    ref : int
        Number of reference lines in center of k-space
    sshift : int
        Sampling shift; index of line to start sampling        

    Returns
    -------
    bim : (kx, ky) array
        Binary image of resulting accelerated sampling pattern   

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)    
    """

    sshift = sshift % acc


    # Generate parallel imaging undersampling pattern

    accBim = np.zeros(dataShape)
    accBim[:,sshift::acc] = 1

    # Generate reference lines pattern
    refBim = np.zeros(dataShape)
    if ref > 0:
        startIndex = int((dataShape[1]-ref) / 2)
        endIndex = startIndex + ref
        refBim[:,startIndex:endIndex]= 2


    imBim = accBim + refBim

    return imBim
    
def ExtractCalData(data, samplingPattern=None, maxReadoutWidth=-1):
    import scipy.ndimage.morphology
    """Extract region of calibration data from an internally calibrated data set.

    Parameters
    ----------
    data : (kx, ky, Nc) array
        accelerated data set with zeros in the unacquired frames.
    samplingPattern : (kx, ky) array
        sampling pattern mask.
        0 = not acquired
        >0 = acquired
        if None, uses np.max(np.abs(data))

    Returns
    -------
    calData : (kx, ky, Nc) array
        calibration data sub matrix

    Notes
    -----
    Code made available for the ISMRM 2015 Sunrise Educational Course

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.
        
    Philip J. Beatty (philip.beatty@gmail.com)
    """
    if samplingPattern is None:
        samplingPattern = np.max(np.abs(data), 2)
    ky_projection = np.max(samplingPattern, axis=0)
    kx_projection = np.max(samplingPattern, axis=1)
    
    ky_contiguous = scipy.ndimage.morphology.binary_opening(ky_projection, structure=np.ones((3,)))    
    kx_contiguous = scipy.ndimage.morphology.binary_opening(kx_projection, structure=np.ones((3,)))    
    
    cal_indx = np.nonzero(kx_contiguous)
    cal_indy = np.nonzero(ky_contiguous)

    kx_cal_bounds = np.arange(np.min(cal_indx), np.max(cal_indx)+1)
    if maxReadoutWidth > 0:
        kx_cal_bounds = np.arange((samplingPattern.shape[0]-maxReadoutWidth)/2, (samplingPattern.shape[0]+maxReadoutWidth)/2)
    
    
    ky_cal_bounds = np.arange(np.min(cal_indy), np.max(cal_indy)+1)
    channelBounds = np.arange(0, data.shape[2])
    
    cal_data = data[np.ix_(kx_cal_bounds, ky_cal_bounds, channelBounds)]
    
    return cal_data