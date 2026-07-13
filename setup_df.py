
import os
import shutil
import numpy as np
import glob
import h5py

import argparse


def generate_config_ini(detd=1, lamb=1.27, detsize=[512, 512]):
    s = f''
    s +=f'[parameters]\n'
    s +=f'detd = {detd}\n'
    s +=f'lambda = {lamb}\n'
    s +=f'detsize = {detsize[0]} {detsize[1]}\n'
    s +=f'pixsize = 0.2\n'
    s +=f'stoprad = 10\n'
    s +=f'polarization = x\n'
    
    s +=f'\n\n[make_detector]\n'
    s +=f'out_detector_file = data/det.h5\n'
    
    s +=f'\n\n[emc]\n'
    s +=f'in_photons_file = data/photons.emc\n'
    s +=f'in_detector_file = make_detector:::out_detector_file\n'
    s +=f'num_div = 6\n'
    s +=f'output_folder = data/\n'
    s +=f'log_file = logs/EMC.log\n'
    s +=f'need_scaling = 1\n'
    s +=f'beta_factor = 1.0\n'
    s +=f'beta_schedule = 2.0 10\n'
    return s
    

    


    
    



if __name__=='__main__':
    parser = argparse.ArgumentParser(description='setup_df.py')

    parser.add_argument("--df-tag", type=str, default='')
    parser.add_argument("--hit-tags", nargs='+', type=str, default='')
    parser.add_argument("--detd", type=float, default=1)
    parser.add_argument("--lamb", type=float, default=1.27)
    
    args = parser.parse_args()


    if not os.path.isdir(args.df_tag):
        print('Make the dragonfly directoy first')
        print()
        print(f'dragonfly.init -t {args.df_tag}')
        print()
        exit()


    h5_files = []
    for hit_tag in args.hit_tags:
        tag_h5_files = glob.glob(f'{hit_tag}/*_i*.h5')
        h5_files += tag_h5_files

    with open(f'{args.df_tag}/data/photons.txt', 'w') as f:
        for h5_file in h5_files:
            f.write(h5_file)
            f.write('\n')

    

    with h5py.File(f'{h5_file}', 'r') as f:
        data_shape = f['/data'].shape
        

    #shutil.copy('./config_DEFAULT.ini', f'{args.df_tag}/config.ini')

    with open(f'{args.df_tag}/config.ini', 'w') as f:
        f.write(
            generate_config_ini(args.detd, args.lamb, data_shape)
        )
        
    print(f'python Dragonfly/utils/convert/h5toemc.py -d /data -l {args.df_tag}/data/photons.txt -o {args.df_tag}/data/photons.emc -c {args.df_tag}/config.ini')
    print(f'dragonfly.utils.make_detector -c {args.df_tag}/config.ini')
    

    


    






