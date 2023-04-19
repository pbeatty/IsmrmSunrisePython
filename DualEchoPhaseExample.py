# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 03:10:36 2015

@author: pbeatty
"""
import numpy as np
import scipy.io as io
import IsmrmSunrise
import Display

def DisplayPhaseDiff(imOP, imIP, title):
    Display.ShowImage2D([imOP, imIP, imOP * np.conj(imIP)], titles=["Out of phase", "In phase", "phase diff"], windowTitle=title)

def GenerateCalImages(calData, imShape):
    lpFilter = (np.mat(np.hamming(calData.shape[0])).T * np.mat(np.hamming(calData.shape[1]))).A
    calIm = IsmrmSunrise.TransformKspaceToImage(calData * lpFilter[:,:,np.newaxis], [0, 1], imShape, preShift=-np.ceil(np.array(calData.shape)*.5))
    return calIm

def ExtractUniformlyAcceleratedData(data, accFactor):
    dataUniformAccel = np.zeros(data.shape, dtype=complex)
    dataUniformAccel[:, 1::accFactor, :] = data[:,1::accFactor, :]
    return dataUniformAccel


def ComputeCcmFromCalIm(calIm, csmMethod):
    csm = csmMethod(calIm)
    ccm = IsmrmSunrise.ComputeChannelCombinationMaps(csm)
    return ccm
    

def Recon(uniformAccelData, accFactor, jerLookup, ccmMethod, ccCalData):
    ccCalIm = GenerateCalImages(ccCalData, imShape = [256, 256])

    ccm = ccmMethod(ccCalIm)
    unmix = IsmrmSunrise.ComputeJerUnmixing(jerLookup, accFactor, ccm, 0.001, False)
    imAlias = IsmrmSunrise.TransformKspaceToImage(uniformAccelData, [0,1])
    im = np.sum(imAlias*unmix, 2)
    return im
    

accelDataOOP = io.loadmat('dual-echo-body-R2-3-1.mat')['acquired_data']
accelDataIP = io.loadmat('dual-echo-body-R2-3-2.mat')['acquired_data']
accFactor = 2

calDataOOP = IsmrmSunrise.ExtractCalData(accelDataOOP, maxReadoutWidth=32)
calDataIP = IsmrmSunrise.ExtractCalData(accelDataIP, maxReadoutWidth=32)
uniformAccelDataOOP = ExtractUniformlyAcceleratedData(accelDataOOP, accFactor)
uniformAccelDataIP = ExtractUniformlyAcceleratedData(accelDataIP, accFactor)


print('Calibration - Compute joint encoding relations')
kernel_shape = [5, 7]
jerLookupOOP = IsmrmSunrise.ComputeJerDataDriven(calDataOOP, kernel_shape)
jerLookupIP = IsmrmSunrise.ComputeJerDataDriven(calDataIP, kernel_shape)



imOOP_MckenzieOOP = Recon(uniformAccelDataOOP, 2, jerLookupOOP, lambda calIm: ComputeCcmFromCalIm(calIm, IsmrmSunrise.EstimateCsmMckenzie), calDataOOP)
imIP_MckenzieOOP = Recon(uniformAccelDataIP, 2, jerLookupIP, lambda calIm: ComputeCcmFromCalIm(calIm, IsmrmSunrise.EstimateCsmMckenzie), calDataOOP)
imIP_MckenzieIP = Recon(uniformAccelDataIP, 2, jerLookupIP, lambda calIm: ComputeCcmFromCalIm(calIm, IsmrmSunrise.EstimateCsmMckenzie), calDataIP)

imOOP_WalshOOP = Recon(uniformAccelDataOOP, 2, jerLookupOOP, lambda calIm: ComputeCcmFromCalIm(calIm, IsmrmSunrise.EstimateCsmWalsh), calDataOOP)
imIP_WalshOOP = Recon(uniformAccelDataIP, 2, jerLookupIP, lambda calIm: ComputeCcmFromCalIm(calIm, IsmrmSunrise.EstimateCsmWalsh), calDataOOP)
imIP_WalshIP = Recon(uniformAccelDataIP, 2, jerLookupIP, lambda calIm: ComputeCcmFromCalIm(calIm, IsmrmSunrise.EstimateCsmWalsh), calDataIP)

imOOP_DvcOOP = Recon(uniformAccelDataOOP, 2, jerLookupOOP, IsmrmSunrise.ComputeCcmDvc, calDataOOP)
imIP_DvcOOP = Recon(uniformAccelDataIP, 2, jerLookupIP, IsmrmSunrise.ComputeCcmDvc, calDataOOP)
imIP_DvcIP = Recon(uniformAccelDataIP, 2, jerLookupIP, IsmrmSunrise.ComputeCcmDvc, calDataIP)

DisplayPhaseDiff(imOOP_MckenzieOOP, imIP_MckenzieOOP, "McKenzie OOP cal")
DisplayPhaseDiff(imOOP_MckenzieOOP, imIP_MckenzieIP, "McKenzie self cal")

DisplayPhaseDiff(imOOP_WalshOOP, imIP_WalshOOP, "Walsh OOP cal")
DisplayPhaseDiff(imOOP_WalshOOP, imIP_WalshIP, "Walsh self cal")

DisplayPhaseDiff(imOOP_DvcOOP, imIP_DvcOOP, "DVC OOP cal")
DisplayPhaseDiff(imOOP_DvcOOP, imIP_DvcIP, "DVC self cal")


Display.BlockOnOpenWindow()



    