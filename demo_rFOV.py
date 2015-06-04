
import numpy as np
import IsmrmSunrise
from Display.Viewers import imshow2d

# <codecell>
# Parameters
noise_scale = 0.05;
kernel_shape = [5, 7]

print 'Loading Ground Truth Information'

#Load Image & Sensitivity Maps
im1 = np.load('im1.npy')
smaps = np.load('smaps.npy')
Rn_normal_8 = np.load('Rn_normal_8.npy')
Rn_broken_8 = np.load('Rn_broken_8.npy')

ncoils = smaps.shape[2]
Rn = Rn_normal_8
im_shape = im1.shape
channel_im = smaps * im1[:,:,np.newaxis]


# <codecell>
# create accelerated data
print 'Creating rFOV Accelerated Data'
noise = noise_scale * np.max(im1) * IsmrmSunrise.GenerateCorrelatedNoise(im_shape, Rn)

data = IsmrmSunrise.TransformImageToKspace(channel_im, [0, 1]) + noise

# halve FOV
data = data[:,0::2,:]
im_shape = data.shape[0:2]

acc_factor = 2;
sp = IsmrmSunrise.GenerateAcceleratedSamplingPattern(im_shape, acc_factor, 20)

data_accel = data * (sp>0)[:,:, np.newaxis]

im_full = IsmrmSunrise.TransformKspaceToImage(data,[0,1])
data_uniform_accel = data_accel * np.logical_or(sp == 1, sp == 3)[:,:, np.newaxis]
im_alias = IsmrmSunrise.TransformKspaceToImage(data_uniform_accel,[0,1])


# pull out cal data
cal_data = IsmrmSunrise.ExtractCalData(data, sp)



# Estimate sensitivitiy maps for channel combination
print 'Calibration - Estimating Coil Sensitivities'

f = (np.mat(np.hamming(cal_data.shape[0])).T * np.mat(np.hamming(cal_data.shape[1]))).A

im_lr = IsmrmSunrise.TransformKspaceToImage(cal_data * f[:,:,np.newaxis], [0, 1], im_full.shape)
csm_walsh = IsmrmSunrise.EstimateCsmWalsh(im_lr)
csm_mckenzie = IsmrmSunrise.EstimateCsmMckenzie(im_lr)
csm_true = smaps[:,64:192,:]

csm_walsh = IsmrmSunrise.NormalizeShadingToSoS(csm_walsh)[0]
csm_mckenzie = IsmrmSunrise.NormalizeShadingToSoS(csm_mckenzie)[0]
csm_true = IsmrmSunrise.NormalizeShadingToSoS(csm_true)[0]

ccm_true = IsmrmSunrise.ComputeChannelCombinationMaps(csm_true)
ccm_mckenzie = IsmrmSunrise.ComputeChannelCombinationMaps(csm_mckenzie)
ccm_walsh = IsmrmSunrise.ComputeChannelCombinationMaps(csm_walsh)


# Create unmixing images
print 'Calibration - Generate Unmixing Images'

jer_lookup_dd = IsmrmSunrise.ComputeJerDataDriven(cal_data, kernel_shape)
cal_im = IsmrmSunrise.TransformKspaceToImage(cal_data, [0,1], 2 * cal_data.shape)
jer_lookup_md = IsmrmSunrise.ComputeJerModelDriven(cal_im, kernel_shape)

num_recons = 5
titles = ['SENSE true csm', 'SENSE walsh csm', 'SENSE mckenzie csm', 'PARS', 'GRAPPA']
unmix = np.zeros([im_shape[0], im_shape[1], ncoils, num_recons], dtype=np.complex)
unmix[:,:,:,0] = IsmrmSunrise.ComputeSenseUnmixing(acc_factor, csm_true, Rn) * acc_factor
unmix[:,:,:,1] = IsmrmSunrise.ComputeSenseUnmixing(acc_factor, csm_walsh, Rn) * acc_factor
unmix[:,:,:,2] = IsmrmSunrise.ComputeSenseUnmixing(acc_factor, csm_mckenzie, Rn) * acc_factor
unmix[:,:,:,3] = IsmrmSunrise.ComputeJerUnmixing(jer_lookup_md, acc_factor, ccm_mckenzie, 0.001, False)
unmix[:,:,:,4] = IsmrmSunrise.ComputeJerUnmixing(jer_lookup_dd, acc_factor, ccm_mckenzie, 0.001, False)


# Perform reconstructions
print 'Perform reconstructions'
im_full = np.abs(np.sum(im_full * ccm_mckenzie, 2))

im_hat = np.zeros([im_shape[0], im_shape[1], num_recons])
im_diff = np.zeros([im_shape[0], im_shape[1], num_recons])


for recon_index in range(num_recons):
    im_hat[:,:,recon_index] = np.abs(np.sum(im_alias * unmix[:,:,:,recon_index], 2))
    im_diff[:,:,recon_index] = np.abs(im_hat[:,:,recon_index] - im_full)

    

imshow2d(im_hat, windowTitle='rFOV image reconstructions', titles=titles)
imshow2d(im_diff, windowTitle='rFOV image reconstruction diffs', titles=titles)
