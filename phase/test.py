import spimage
import h5py
import numpy as np
import scipy
import matplotlib.pyplot as plt
import time

t1 = time.time()




intens_file = '/gpfs/exfel/u/usr/SPB/202501/p006933/Shared/dfly-p6933/r267r268_0003/data/output_030.h5'

with h5py.File(intens_file, 'r') as f:
    intens = f['/intens'][...]


intens = np.squeeze(intens)
intens = intens[45:316, 45:316, 45:316]
nx,ny,nz = intens.shape


# blocks  = 5
# niter_hio = 20*blocks
# niter_er = 5*blocks
# niter_total = niter_hio+niter_er
beta = 0.9


algos = ['hio', 'er']*50
n_iters = [20, 2]*50


R = spimage.Reconstructor()

R.set_intensities(intens)
R.set_number_of_iterations(sum(n_iters))
R.set_number_of_outputs_images(50)
R.set_number_of_outputs_scores(50)
R.set_initial_support(radius=60)
#R.set_support_algorithm("static", number_of_iterations=sum(n_iters))

R.set_support_algorithm("area", update_period=22, blur_init=3, blur_final=1, area_init=1, area_final=0.5, number_of_iterations=sum(n_iters))


for algo, n_iter in zip(algos, n_iters):
    if algo=='hio':
        R.append_phasing_algorithm(algo, beta_init=beta, beta_final=beta, number_of_iterations=n_iter)
    else:
        R.append_phasing_algorithm(algo, number_of_iterations=n_iter)



print('Starting reconstruction.')
output=R.reconstruct()

print(output.keys())
for key in output.keys():
    print(key, type(output[key]))
    


t2= time.time()
# Collect results

with h5py.File(f'./phase-out.h5', 'w') as f:
    f['/recons'] = output['real_space']
    f['/fourier']= output['fourier_space']
    f['/support']= output['support']
    f['/rerror'] = output["real_error"]
    f['/ferror'] = output["fourier_error"]
    f['/iter_images'] = output["iteration_index_images"]
    f['/iter_scores'] = output["iteration_index_scores"]
    f['/mask'] = output["mask"]
    f['/support_size'] = output["support_size"]
    f['/t1'] = t1
    f['/t2'] = t2









