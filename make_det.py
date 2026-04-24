

import numpy as np
import extra_data
import extra_geom
import h5py

import argparse




def main():

    parser = argparse.ArgumentParser(description='make_mask.py')

    parser.add_argument("--part-1", type=int, default=1)

    parser.add_argument("--rebin", type=int, default=1)
    parser.add_argument("--detd", type=float, default=1)
    parser.add_argument("--lamb", type=float, default=1)
    parser.add_argument("--tag", type=str, default='tag')
    parser.add_argument("--crop-size", type=int, nargs=2, metavar=('NY','NX'), default=[1264, 1112])

    args = parser.parse_args()

    assert args.crop_size[1]%2==0, 'crop-size[1] needs to be even'
    assert args.crop_size[0]%2==0, 'crop-size[0] needs to be even'
    assert args.rebin in [1,2,4,8], 'rebin must be either 1,2,4,8'

    xstart, xend = 1112//2 - args.crop_size[1]//2, 1112//2 + args.crop_size[1]//2
    ystart, yend = 1266//2 - args.crop_size[0]//2, 1266//2 + args.crop_size[0]//2




    GEOM_FNAME = './det/agipd_p008039_r0014_v16.geom'
    MASK_FNAME = './det/mask_hvoff_20250311.h5'



    ref_geom = extra_geom.AGIPD_1MGeometry.from_crystfel_geom(GEOM_FNAME)



    with h5py.File(MASK_FNAME, 'r') as f:
        mask = f['/entry_1/data_1/mask'][...]

    assem = np.ones( (1266, 1112) )

    ref_geom.position_modules(mask, out=assem)

    assem*=2

    assem = assem[ystart:yend, xstart:xend]

    assem_height, assem_width = assem.shape

    rebin_height, rebin_width  = assem_height//args.rebin, assem_width//args.rebin

    assem_rebin = assem.reshape(rebin_height, args.rebin, rebin_width, args.rebin).sum(axis=(1,3))





    if args.part_1:
        with open(f'./det/config_{args.tag}.ini', 'w') as f:
            f.write('#\n')
            f.write('[parameters]\n')
            f.write(f'detd = {args.detd}\n')
            f.write(f'lambda = {args.lamb}\n')
            f.write(f'detsize = {rebin_height} {rebin_width}\n')
            f.write(f'pixsize = 0.2\n')
            f.write(f'stoprad = 10\n')
            f.write(f'polarization = x\n')

            f.write('\n\n')
            f.write('[make_detector]\n')
            f.write(f'out_detector_file = ./det_{args.tag}.h5 \n')

            f.write('\n\n')
            f.write('[emc]\n')
            f.write(f'in_photons_file = data/photons.emc\n')
            f.write(f'in_detector_file = make_detector:::out_detector_file\n')
            f.write(f'num_div = 6\n')
            f.write(f'output_folder = data/\n')
            f.write(f'log_file = logs/EMC.log\n')
            f.write(f'need_scaling = 1\n')
            f.write(f'beta_factor = 1.0\n')
            f.write(f'beta_schedule = 2.0 10\n')

        print('cd det')
        print(f'dragonfly.utils.make_detector -c ./config_{args.tag}.ini --yes')
        print('cd ..')

        p2cmd = 'python make_det.py --part-1 0'
        p2cmd += f' --rebin {args.rebin}'
        p2cmd += f' --crop-size {args.crop_size[0]} {args.crop_size[1]}'
        p2cmd += f' --tag {args.tag}'
        print(p2cmd)
        return




    with h5py.File(f'./det/det_{args.tag}.h5', 'a') as f:
        f['/mask'][...] = assem_rebin.flatten()
        f['/mask_square'] = assem_rebin









if __name__ == '__main__':
    main()


