




import numpy as np
import h5py
import argparse
import glob
import os







def main():

    parser = argparse.ArgumentParser(description='prep_recon.py')
    parser.add_argument("--recon-dir", type=str) ## recon_0001
    parser.add_argument("--hit-tags", nargs='+', type=str) ##r0307_cp512 r0306_cp512
    parser.add_argument("--config-ini", type=str)

    args = parser.parse_args()


    h5files = []

    for tag in args.hit_tags:
        path = os.path.join('hit_images', tag, '*.h5')
        h5files = h5files+list(glob.glob(path))



    with open(f'./{args.recon_dir}/data/hit_h5s.txt', 'w') as f:
        for h5file in h5files:
            f.write(h5file)
            f.write('\n')


    print(f'python Dragonfly/utils/convert/h5toemc.py -d /data -l {args.recon_dir}/data/hit_h5s.txt -o {args.recon_dir}/data/photons.emc -c {args.config_ini}')































if __name__ =="__main__":
    main()
