
import os
import shutil
import numpy as np
import glob
import h5py

import argparse



if __name__=='__main__':
    parser = argparse.ArgumentParser(description='setup_df.py')

    parser.add_argument("--df-tag", type=str, default='')
    parser.add_argument("--hit-tags", nargs='+', type=str, default='')

    args = parser.parse_args()


    if not os.path.isdir(args.df_tag):
        print('Make the dragonfly directoy first')
        print()
        print(f'dragonfly.init -t {args.df_tag}')
        print()
        exit()

    shutil.copy('./config_DEFAULT.ini', f'{args.df_tag}/config.ini')

    h5_files = []
    for tag in args.hit_tags:
        tag_h5_files = glob.glob(f'{tag}/*.h5')
        h5_files += tag_h5_files

    # mapped_h5_files = list(map( lambda s: '../../'+s, h5_files))
    # mapped_h5_files = map( lambda s: ''+s, h5_files)


    with open(f'{args.df_tag}/data/photons.txt', 'w') as f:
        for h5_file in h5_files:
            f.write(h5_file)
            f.write('\n')


    with h5py.File(f'{h5_file}', 'r') as f:
        rebin_ds = f['/rebin']
        rebin = rebin_ds[()]
        crop_x = f['/crop-size'][1]
        crop_y = f['/crop-size'][0]

            
    print(f'Created photons.txt list in {args.df_tag}/data')
    print('You need to make detector and convert h5 files')
    print()
    print(f'python Dragonfly/utils/convert/h5toemc.py -d /data -l {args.df_tag}/data/photons.txt -o {args.df_tag}/data/photons.emc -c {args.df_tag}/config.ini')
    print(f'dragonfly.utils.make_detector -c {args.df_tag}/config.ini')
    print(f'python make_det.py --df-tag {args.df_tag} --rebin {rebin} --crop-size {crop_y} {crop_y}')


    # print(f'sbatch submit_slurm.sh {args.df_tag}')











