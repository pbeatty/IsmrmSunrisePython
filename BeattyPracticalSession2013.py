# -*- coding: utf-8 -*-

# ISMRM Sunrise Practical Session, Parallel Imaging Part I
#
# This document contains the first set of practical exercises for the
# ISMRM course on parallel imaging.

## Exercise Data
#
# Exercise ground truth information is found in im1.mat (brain image), smaps_phantom.mat
# (sensitivity maps) and noise_covariances.mat (noise covariance matrices).
#
# We start by clearing the workspace, loading this ground truth information
# and setting a few parameters from this.
import numpy as np
import scipy.ndimage as spImage
import matplotlib as mpl
from Display.Viewers import imshow2d
import IsmrmSunrise

# <codecell>
print "Loading Ground Truth Information"
im1 = np.load('im1.npy')
smaps = np.load('smaps.npy')
Rn_normal_8 = np.load('Rn_normal_8.npy')
Rn_broken_8 = np.load('Rn_broken_8.npy')
imshow2d(im1, windowTitle='Ground Truth Image')
imshow2d(smaps, windowTitle='Coil Sensitivities', titles='Sensitivity', maxNumInRow=4)
print "done imshow2d"

numChannels = smaps.shape[2]

Rn = Rn_normal_8

nx = im1.shape[0]
ny = im1.shape[1]

# <codecell>
# Data Simulation
#
# Let's use our ground truth data to simulate some data
#
print "Simulating unaccelerated data"
channelIm = smaps * im1[:,:,np.newaxis]

imshow2d(channelIm, windowTitle= 'Image multiplied by coil sensitivities', titles='Channel', maxNumInRow=4)

noiseScale = 0.1
noise = noiseScale * np.max(im1) * IsmrmSunrise.GenerateCorrelatedNoise(im1.shape, Rn)

data = IsmrmSunrise.TransformImageToKspace(channelIm, [0, 1]) + noise


# <codecell>
# Prewhiten
# 
# Let's start by prewhitening so that we don't have to contend with the
# noise covariance matrix.
#
print "Prewhiten data and coil sensitivities"
dmtx = IsmrmSunrise.ComputeNoiseDecorrelationMatrixFromCovarianceMatrix(Rn)

csmTrue = IsmrmSunrise.ApplyNoiseDecorrelationMatrix(smaps, dmtx)
data = IsmrmSunrise.ApplyNoiseDecorrelationMatrix(data, dmtx)

Rn = np.eye(numChannels);


# <codecell>
## Channel Combination
#
# Let's use our ground truth data to perform an SNR-optimal channel
# combination
print "Perform SNR-optimal channel combination"

imFull = IsmrmSunrise.TransformKspaceToImage(data, [0, 1])
ccmRoemerOptimal = IsmrmSunrise.ComputeChannelCombinationMaps(csmTrue, np.eye(numChannels))

imRoemerOptimal = np.abs(np.sum(imFull * ccmRoemerOptimal, 2))

# How does this compare to our ground-truth image?
imshow2d([im1, imRoemerOptimal, imRoemerOptimal - im1], windowTitle='Comparison of Ground Truth image to SNR-optimal channel combination', titles=["Ground Truth", "Roemer Optimal", "Difference"])

##
# The noise level varies slightly from pixel-to-pixel.  Let's make a map of
# this
noiseMap = IsmrmSunrise.ComputeNoiseAmplification(ccmRoemerOptimal, np.eye(numChannels))
imshow2d(noiseMap, windowTitle="Noise Map", colormap=mpl.cm.jet)

##
# How does this compare to a root-sum-of-squares (SOS) reconstruction?
imSoS = IsmrmSunrise.ComputeRootSumOfSquaresChannelCombination(imFull)
imshow2d([imRoemerOptimal, imSoS, imRoemerOptimal-imSoS], windowTitle='SoS compared to SNR-optimal channel combination', titles=["Roemer Optimal", "SoS", "Difference"])


# <codecell>
##
# Looks like we have a scaling and/or shading issue that makes it hard to
# do this comparison. Let's normalize to SOS shading
print "Compare after normalizing to SoS shading"
ccmRoemerOptimal, shadingCorrectionIm = IsmrmSunrise.NormalizeShadingToSoS(ccmRoemerOptimal)
imRoemerOptimal = np.abs(np.sum(imFull * ccmRoemerOptimal, 2));
imTrue = shadingCorrectionIm * im1;

imshow2d([imTrue, imRoemerOptimal, imSoS], windowTitle="After correcting for shading differences", titles=["Ground Truth", "Roemer Optimal", "SoS"])
imshow2d([imRoemerOptimal - imTrue, imSoS-imTrue], windowTitle="Difference Images after correcting for shading differences", titles=["Roemer Optimal", "SoS"])


# <codecell>
##
# SOS channel combination aligns the phase of the background noise before
# summing, leading to a DC ofset in these pixels.  Let's try channel
# combination based on coil sensitivity estimates from some low resolution
# calibration data.
#
print "Try low res channel combination"
calx = 32
caly = 32
calShape = np.array([calx, caly])
calNoiseScale = 0.1;

calData = IsmrmSunrise.TransformImageToKspace(channelIm, dim=[0,1], kShape = calShape)
noise = calNoiseScale * np.max(im1) * IsmrmSunrise.GenerateCorrelatedNoise(calShape, Rn)
calData = calData + noise

calData = IsmrmSunrise.ApplyNoiseDecorrelationMatrix(calData, dmtx);

f = (np.mat(np.hamming(calShape[0])).T * np.mat(np.hamming(calShape[1]))).A
filteredCalData = calData * f[:,:,np.newaxis]

calIm = IsmrmSunrise.TransformKspaceToImage(filteredCalData, [0, 1], im1.shape);

# Use a circular region of support for pixels
pixelMask = ((np.sum(np.abs(smaps),2))>0).astype(np.float)
pixelMask = pixelMask[:,:, np.newaxis]
calIm = calIm * pixelMask

csmWalsh = IsmrmSunrise.EstimateCsmWalsh(calIm)
csmMckenzie = IsmrmSunrise.EstimateCsmMckenzie(calIm)

csmTrue = IsmrmSunrise.NormalizeShadingToSoS(csmTrue)[0]
csmWalsh = IsmrmSunrise.NormalizeShadingToSoS(csmWalsh)[0]
csmMckenzie = IsmrmSunrise.NormalizeShadingToSoS(csmMckenzie)[0]

ccmMckenzie = IsmrmSunrise.ComputeChannelCombinationMaps(csmMckenzie)
ccmWalsh = IsmrmSunrise.ComputeChannelCombinationMaps(csmWalsh)

imMckenzie = np.sum(imFull * ccmMckenzie, 2)
imWalsh = np.sum(imFull * ccmWalsh, 2)

imshow2d([imTrue, imRoemerOptimal, imSoS, imWalsh, imMckenzie], 
         windowTitle='Comparison of channel combination methods', titles=["source image", "true csm", "SoS", "Walsh csm", "McKenzie csm"])
imshow2d([imRoemerOptimal-imTrue, imSoS-imTrue, np.abs(imWalsh)-np.abs(imTrue), np.abs(imMckenzie)-np.abs(imTrue)], 
          windowTitle='Difference images for comparison of channel combination methods', titles=["true csm", "SoS", "Walsh csm", "McKenzie csm"])


#imshow2d(csmWalsh, windowTitle="csmWalsh")
#imshow2d(csmTrue, windowTitle="csmTrue")


# <codecell>
## Create Accelerated Data
#
print "Create Accelerated Data"
accFactor = 4;
samplingPattern = IsmrmSunrise.GenerateAcceleratedSamplingPattern(im1.shape, accFactor, 0)
samplingMask = np.logical_or(samplingPattern == 1,samplingPattern == 3).astype(np.float)
dataAccel = data * samplingMask[:,:,np.newaxis]
imAlias = IsmrmSunrise.TransformKspaceToImage(dataAccel, [0,1])

imshow2d(imAlias, maxNumInRow=4, windowTitle='Aliased Images', titles='channel')
## Create Data Driven & Model Driven Joint Encoding Relations
#
print "Create Joint Encoding Relations"
kernelShape = [5, 7]
jerLookupDd = IsmrmSunrise.ComputeJerDataDriven(calData, kernelShape)
unfilteredCalIm = IsmrmSunrise.TransformKspaceToImage(calData, [0, 1], imShape = 2 * calData.shape)
jerLookupMd = IsmrmSunrise.ComputeJerModelDriven(unfilteredCalIm, kernelShape)
# <codecell>
# Use Various Calibration Approaches to Create Unmixing Images
#
print "Create Unmixing Images"
numRecons = 4;
titles = ['SENSE true csm', 'SENSE estimated csm', 'PARS', 'GRAPPA']

unmix = np.zeros([nx, ny, numChannels, numRecons], dtype=np.complex)
unmix[:,:,:,0] = IsmrmSunrise.ComputeSenseUnmixing(accFactor, csmTrue, np.eye(numChannels), 0) * accFactor
unmix[:,:,:,1] = IsmrmSunrise.ComputeSenseUnmixing(accFactor, csmMckenzie, np.eye(numChannels), 0) * accFactor
print 'Done ComputeSenseUnmixing'
unmix[:,:,:,2] = IsmrmSunrise.ComputeJerUnmixing(jerLookupMd, accFactor, ccmMckenzie, 0.0, False)
unmix[:,:,:,3] = IsmrmSunrise.ComputeJerUnmixing(jerLookupDd, accFactor, ccmMckenzie, 0.0, False)
print 'done ComputeJerUnmixing'

#
# SENSE unmixing
imshow2d(unmix[:,:,:,0], maxNumInRow=4, titles='Channel', windowTitle="Unmixing coefficients from true sensitivities")

# SENSE unmixing with estimated coil sensitivity maps
imshow2d(unmix[:,:,:,1], maxNumInRow=4, titles='Channel', windowTitle="Unmixing coefficients from estimated sensitivities")

# PARS unmixing
imshow2d(unmix[:,:,:,2], maxNumInRow=4, titles='Channel', windowTitle="Unmixing coefficients from PARS")

# GRAPPA unmixing
imshow2d(unmix[:,:,:,3], maxNumInRow=4, titles='Channel', windowTitle="Unmixing coefficients from GRAPPA")


# Apply and Analyze Reconstructions
print "Apply and Analyze Reconstructions"
matrixShape = [nx, ny, numRecons]
aem = np.zeros(matrixShape, dtype=np.complex)
gmap = np.zeros(matrixShape, dtype=np.complex)
im_hat = np.zeros(matrixShape, dtype=np.complex)
im_diff = np.zeros(matrixShape, dtype=np.complex)

signalMask = spImage.morphology.binary_closing(im1>100.0, structure = np.ones((5,5))).astype(np.int)

for reconIndex in range(numRecons):
    aem[:,:,reconIndex] = IsmrmSunrise.ComputeAliasingEnergyMap(signalMask, csmTrue, unmix[:,:,:,reconIndex], accFactor)
    gmap[:,:,reconIndex] = IsmrmSunrise.ComputeGmap(unmix[:,:,:,reconIndex], ccmRoemerOptimal, accFactor, Rn)
    im_hat[:,:,reconIndex] = np.sum(imAlias * unmix[:,:,:,reconIndex], 2)
    im_diff[:,:,reconIndex] = np.abs(im_hat[:,:,reconIndex]) - np.abs(imTrue)

# aliasing energy maps
imshow2d(aem, titles=titles, windowTitle="Aliasing Energy Maps, R=4", colormap=mpl.cm.jet)
#ismrm_imshow(aem, [0 0.1], [], titles); colormap(jet);

# g-factor (relative noise amplification) maps
imshow2d(gmap, titles=titles, windowTitle="G-factor maps, R=4", colormap=mpl.cm.jet)
#ismrm_imshow(gmap, [0 6], [], titles); colormap(jet);

# reconstructed images
imshow2d(im_hat,  windowTitle='Reconstructed Images, R=4', titles=titles)

# difference images
imshow2d(im_diff, windowTitle='Difference Images, R=4', titles=titles)