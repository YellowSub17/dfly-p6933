import spimage
import h5py
import numpy as np
import scipy
import matplotlib.pyplot as plt
import time
import argparse
import os
import sys
import shutil
import logging



def parse_recipe(file_path="PHASE_RECIPE.txt"):
    phase_params = {}
    algos = []
    niters = []
    kwargss = []
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The recipe file '{file_path}' does not exist.")
        
    with open(file_path, "r") as f:
        lines = f.readlines()

    stack = []
    current_instructions = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        tokens = line.split()
        
        # Scenario A: Global Parameter (e.g., "wavelength=1.54" or "support_type=circle")
        # Identified by lack of numeric prefix & containing an '=' sign in the first token
        if "=" in tokens[0] and not tokens[0].split("=")[0].isdigit():
            for param in tokens:
                if "=" in param:
                    key, value = param.split("=")
                    try:
                        phase_params[key] = float(value)
                    except ValueError:
                        # Fallback if value is a string (like support_type=circle)
                        phase_params[key] = value
            continue

        # Scenario B: Start of a block (e.g., "6 {")
        if len(tokens) == 2 and tokens[1] == "{":
            multiplier = int(tokens[0])
            stack.append((multiplier, current_instructions))
            current_instructions = []
            continue
            
        # Scenario C: End of a block ("}")
        if tokens[0] == "}":
            if not stack:
                raise ValueError("Mismatched closing bracket '}' in recipe file.")
                
            multiplier, parent_instructions = stack.pop()
            for _ in range(multiplier):
                parent_instructions.extend(current_instructions)
            
            current_instructions = parent_instructions
            continue
            
        # Scenario D: Standard instruction line (e.g., "20 HIO beta_init=0.9")
        try:
            n_iter = int(tokens[0])
        except ValueError:
            raise ValueError(f"Invalid line format. Expected iterations (integer), got: '{tokens[0]}'")
            
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
            
        current_instructions.append((algo, n_iter, kwargs))

    if stack:
        raise ValueError("Missing closing bracket '}' in recipe file.")

    for algo, n_iter, kwargs in current_instructions:
        algos.append(algo)
        niters.append(n_iter)
        kwargss.append(kwargs)
        
    return phase_params, algos, niters, kwargss


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='phase_recon.py -- Take a dragonfly recon and phase it.')
    parser.add_argument("--df-tag", type=str, default='')
    parser.add_argument("--rec-file", type=str, default='./PHASE_RECIPE.txt')
    #parser.add_argument("--output-n", type=int, default=10)
    
    
    
    args = parser.parse_args()

    count = 1
    while os.path.exists(f'./{args.df_tag}/phase_{count:04}/'):
        count+=1

    PHASE_DIR = f'./{args.df_tag}/phase_{count:04}/'
    os.makedirs(PHASE_DIR, exist_ok=True)
    shutil.copy(args.rec_file, f'{PHASE_DIR}/{args.df_tag}_phase_{count:04}_recipe.txt')
    
    phase_params, algos, n_iters, kwargss = parse_recipe(f'{PHASE_DIR}/{args.df_tag}_phase_{count:04}_recipe.txt')

    inten_n = int(phase_params['inten_n'])
    output_n = int(phase_params['output_n'])
    
    
    
    shutil.copy(f'./{args.df_tag}/data/output_{inten_n:03}.h5',  f'./{PHASE_DIR}/inten_input.h5')
    
    with h5py.File(f'./{PHASE_DIR}/inten_input.h5', 'r') as f:
        intens = f['/intens'][...]
        

    intens = np.squeeze(intens)
   
    nx,ny,nz = intens.shape


    

    # --- FORCE THE INTERNAL LOGGER TO OUTPUT TO TERMINAL ---
    recon_logger = logging.getLogger('RECONSTRUCTOR')
    recon_logger.setLevel(logging.INFO)  # Or logging.DEBUG if you want every tiny detail
    
    # Create a stream handler that pushes directly to your standard terminal output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Apply a clean, scannable format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add it directly to the reconstructor's logger
    recon_logger.addHandler(console_handler)
    
    # Stop the log from propagating up to a broken root logger
    recon_logger.propagate = False
    # --------------------------------
    
    R = spimage.Reconstructor()
    R.set_intensities(intens)
    R.set_number_of_iterations(sum(n_iters))
    R.set_number_of_outputs_images(output_n)
    R.set_number_of_outputs_scores(output_n)
    R.set_initial_support(radius=phase_params['radius'])
    
    #R.set_support_algorithm("static", number_of_iterations=sum(n_iters))
    if phase_params['method']=='area':
        R.set_support_algorithm('area', update_period=int(phase_params['update_period']), 
                            blur_init=float(phase_params['blur_init']), blur_final=float(phase_params['blur_final']),
                            area_init=float(phase_params['area_init']), area_final=float(phase_params['area_final']),
                            center_image=bool(phase_params['center_image']))
    else:
        R.set_support_algorithm("static", number_of_iterations=sum(n_iters))
        
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
    
    