import spimage
import h5py
import numpy as np
import scipy
import matplotlib.pyplot as plt



intens_file = '/gpfs/exfel/u/usr/SPB/202501/p006933/Shared/dfly-p6933/testing_512rb2_0001/data/output_010.h5'

with h5py.File(intens_file, 'r') as f:
    intens = f['/intens'][...]

intens = np.squeeze(intens)
nx,ny,nz = intens.shape

# plt.figure()
# plt.imshow(intens[nx//2, :, :])
# plt.show()


niter_hio = 20
niter_er = 5
niter_total = niter_hio+niter_er
beta = 0.9



R = spimage.Reconstructor()

R.set_intensities(intens)
R.set_number_of_iterations(niter_total)
R.set_number_of_outputs_images(5)
R.set_number_of_outputs_scores(5)
R.set_initial_support(radius=60)
R.set_support_algorithm("static", number_of_iterations=niter_total)
R.append_phasing_algorithm("hio", beta_init=beta, beta_final=beta, number_of_iterations=niter_hio)
R.append_phasing_algorithm("er", number_of_iterations=niter_er)



print('Starting reconstruction.')
output=R.reconstruct()



# Collect results

with h5py.File('./phase-out.h5', 'w') as f:
    f['/recons'] = output['real_space']
    f['/fourier']= output['fourier_space']
    f['/support']= output['support']
    f['/rerror'] = output["real_error"]
    f['/ferror'] = output["fourier_error"]









