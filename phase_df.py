import spimage
import h5py
import numpy as np
import scipy
import matplotlib.pyplot as plt
import time
import argparse
import os
import shutil

def parse_recipe(file_path="PHASE_RECIPE.txt"):
    algos = []
    niters = []
    kwargss = []
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The recipe file '{file_path}' does not exist.")
        
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Stack to keep track of loop structures
    # Each entry will be: [multiplier, [list_of_parsed_instructions]]
    stack = []
    # This holds the current level of instructions we are writing to
    current_instructions = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        tokens = line.split()
        
        # Scenario 1: Start of a block (e.g., "6 {")
        if len(tokens) == 2 and tokens[1] == "{":
            multiplier = int(tokens[0])
            # Save the outer context and start a fresh sub-context
            stack.append((multiplier, current_instructions))
            current_instructions = []
            continue
            
        # Scenario 2: End of a block ("}")
        if tokens[0] == "}":
            if not stack:
                raise ValueError("Mismatched closing bracket '}' in recipe file.")
                
            multiplier, parent_instructions = stack.pop()
            # Repeat the block's content and add it to the parent level
            for _ in range(multiplier):
                parent_instructions.extend(current_instructions)
            
            # Reset current context back to the parent level
            current_instructions = parent_instructions
            continue
            
        # Scenario 3: Standard instruction line (e.g., "20 HIO..." or "40 ER")
        n_iter = int(tokens[0])
        algo = tokens[1].lower()
        
        kwargs = {}
        for param in tokens[2:]:
            if "=" in param:
                key, value = param.split("=")
                try:
                    kwargs[key] = float(value)
                except ValueError:
                    kwargs[key] = value
                    
        if algo == "hio":
            kwargs.setdefault("beta_init", 0.9)
            kwargs.setdefault("beta_final", 0.5)
            
        # Store the individual parsed step as a tuple
        current_instructions.append((algo, n_iter, kwargs))

    if stack:
        raise ValueError("Missing closing bracket '}' in recipe file.")

    # Unpack the final flat list of instructions into three distinct lists
    for algo, n_iter, kwargs in current_instructions:
        algos.append(algo)
        niters.append(n_iter)
        kwargss.append(kwargs)
        
    return algos, niters, kwargss



if __name__=='__main__':

    parser = argparse.ArgumentParser(description='phase_recon.py -- Take a dragonfly recon and phase it.')
    parser.add_argument("--df-tag", type=str, default='')
    parser.add_argument("--inten-n", type=int, default=10)
    parser.add_argument("--output-n", type=int, default=10)
    parser.add_argument("--support-r", type=float, default=60)
    
    
    args = parser.parse_args()

    count = 1
    while os.path.exists(f'./{args.df_tag}/phase_{count:04}/'):
        count+=1

    PHASE_DIR = f'./{args.df_tag}/phase_{count:04}/'
    
    os.makedirs(PHASE_DIR, exist_ok=True)


    shutil.copy('./PHASE_RECIPE.txt', f'{PHASE_DIR}/PHASE_RECIPE.txt')
    
    
    
    shutil.copy(f'./{args.df_tag}/data/output_{args.inten_n:03}.h5',  f'./{PHASE_DIR}/inten_input.h5')
    
    with h5py.File(f'./{PHASE_DIR}/inten_input.h5', 'r') as f:
        intens = f['/intens'][...]

    intens = np.squeeze(intens)
   
    nx,ny,nz = intens.shape
    
    
    algos, n_iters, kwargss = parse_recipe(f'{PHASE_DIR}/PHASE_RECIPE.txt')
    
    R = spimage.Reconstructor()
    R.set_intensities(intens)
    R.set_number_of_iterations(sum(n_iters))
    R.set_number_of_outputs_images(args.output_n)
    R.set_number_of_outputs_scores(args.output_n)
    R.set_initial_support(radius=60)
    
    #R.set_support_algorithm("static", number_of_iterations=sum(n_iters))
    R.set_support_algorithm("area", update_period=22, blur_init=3, blur_final=1, area_init=1, area_final=0.5, number_of_iterations=sum(n_iters))

    for algo, n_iter, kwargs in zip(algos, n_iters, kwargss):
        R.append_phasing_algorithm(algo, number_of_iterations=n_iter, **kwargs)
        

    print('Starting reconstruction.')
    output=R.reconstruct()
    
    print(output.keys())
    for key in output.keys():
        print(key, type(output[key]))
        
    
    # Collect results
    
    with h5py.File(f'{PHASE_DIR}/results.h5', 'w') as f:
        f['/recons'] = output['real_space']
        f['/fourier']= output['fourier_space']
        f['/support']= output['support']
        f['/rerror'] = output["real_error"]
        f['/ferror'] = output["fourier_error"]
        f['/iter_images'] = output["iteration_index_images"]
        f['/iter_scores'] = output["iteration_index_scores"]
        f['/mask'] = output["mask"]
        f['/support_size'] = output["support_size"]
    
    
    
  


if False:
    
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
    
    
    
    
    
    
    
    
    
