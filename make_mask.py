

import numpy as np
import extra_data
import extra_geom
import h5py

import argparse




if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='make_mask.py')
    parser.add_argument("--rebin", type=int, default=1)
    parser.add_argument("--tag", type=str, default='')
    parser.add_argument("--crop-size", type=int, nargs=2, metavar=('NY','NX'), default=[1264, 1112])

    args = parser.parse_args()

    assert args.crop_size[1]%2==0, 'crop-size[1] needs to be even'
    assert args.crop_size[0]%2==0, 'crop-size[0] needs to be even'
    assert args.rebin in [1,2,4,8], 'rebin must be either 1,2,4,8'

    if args.tag != '':
        args.tag = '_'+args.tag

    xstart, xend = 1112//2 - args.crop_size[1]//2, 1112//2 + args.crop_size[1]//2
    ystart, yend = 1266//2 - args.crop_size[0]//2, 1266//2 + args.crop_size[0]//2







    GEOM_FNAME = './geom/agipd_p008039_r0014_v16.geom'
    MASK_FNAME = './geom/mask_hvoff_20250311.h5'



    ref_geom = extra_geom.from_crystfel_geom(GEOM_FNAME)



    with h5py.File(MASK_FNAME, 'r') as f:
        mask = f['/entry_1/data_1/mask'][...]

    assem = np.ones( (1266, 1112) )

    ref_geom.position_modules(mask, out=assem)

    assem*=2

    assem = assem[0,0,ystart:yend, xstart:xend]

    assem_height, assem_width = assem.shape

    rebin_height, rebin_width  = assem_height//args.rebin, assem_width//args.rebin

    assem_rebin = assem.reshape(rebin_height, args.rebin, rebin_width, args.rebin).sum(axis=(1,3))


    with h5py.File(f'./geom/mask{args.tag}.h5', 'w') as f:
        f['/mask'] = assem_rebin.flatten()
        f['/rebin'] = args.rebin
        f['/crop-size'] = args.crop_size










