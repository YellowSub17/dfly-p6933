

import numpy as np
import extra_data
import extra_geom
import h5py

import argparse

# tiles:                     0            1            2            3            4            5            6            7   | modules
det_edges = np.array([[[1178,   16],[1178,   82],[1178,  148],[1178,  214],[1178,  280],[1178,  346],[1178,  412],[1178,  478]],# 0
                  [[1020,   16],[1020,   82],[1020,  148],[1020,  214],[1021,  280],[1021,  346],[1021,  412],[1021,  478]],# 1
                  [[ 863,   16],[ 863,   82],[ 864,  148],[ 864,  214],[ 865,  280],[ 865,  346],[ 866,  412],[ 866,  478]],# 2
                  [[ 706,   16],[ 706,   82],[ 707,  148],[ 707,  214],[ 707,  280],[ 708,  346],[ 708,  412],[ 709,  478]],# 3
                  [[ 544,    0],[ 544,   66],[ 544,  132],[ 544,  198],[ 545,  264],[ 545,  330],[ 545,  396],[ 545,  462]],# 4
                  [[ 386,    0],[ 387,   66],[ 387,  132],[ 387,  198],[ 387,  264],[ 388,  330],[ 388,  396],[ 388,  462]],# 5
                  [[ 231,    1],[ 231,   67],[ 231,  133],[ 231,  199],[ 231,  265],[ 231,  331],[ 231,  397],[ 231,  463]],# 6
                  [[  88,    7],[  88,   73],[  88,  139],[  88,  205],[  88,  271],[  88,  337],[  88,  403],[  88,  469]],# 7
                  [[ 466,  546],[ 466,  612],[ 466,  678],[ 466,  744],[ 466,  810],[ 467,  876],[ 467,  942],[ 467, 1008]],# 8
                  [[ 308,  547],[ 308,  613],[ 309,  679],[ 309,  745],[ 309,  811],[ 309,  877],[ 309,  943],[ 310, 1009]],# 9
                  [[ 152,  547],[ 152,  613],[ 152,  679],[ 152,  745],[ 152,  811],[ 152,  877],[ 152,  943],[ 152, 1009]],#10
                  [[   0,  546],[   0,  612],[   0,  678],[   0,  744],[   0,  810],[   0,  876],[   0,  942],[   0, 1008]],#11
                  [[1089,  563],[1090,  629],[1090,  695],[1091,  761],[1091,  827],[1092,  893],[1093,  959],[1093, 1025]],#12
                  [[ 939,  567],[ 939,  633],[ 940,  699],[ 940,  765],[ 940,  831],[ 941,  897],[ 941,  963],[ 941, 1029]],#13
                  [[ 782,  567],[ 783,  633],[ 783,  699],[ 784,  765],[ 784,  831],[ 784,  897],[ 785,  963],[ 785, 1029]],#14
                  [[ 626,  567],[ 627,  633],[ 627,  699],[ 627,  765],[ 627,  831],[ 628,  897],[ 628,  963],[ 628, 1029]],#15
                 ], dtype=int)

def assembleImage(not_assembled_image):
    """Assembles a (16, 512, 128) array into a (1306, 1093) image."""
    #ret_img = np.full((1306, 1093),np.nan)
    ret_img = np.full((1306, 1093),  1)
    for m_nr, module in enumerate(not_assembled_image):
        trafo = np.rot90(module, axes=(0, 1)) if m_nr<8 else np.rot90(module, axes=(1, 0))
        for t_nr in range(8):
            ref_y, ref_x = det_edges[m_nr, t_nr]
            ret_img[ref_y:ref_y+128, ref_x:ref_x+64] = trafo[:, t_nr*64:(t_nr+1)*64]
    return ret_img




def main():

    parser = argparse.ArgumentParser(description='make_mask.py')

    parser.add_argument("--part-1", type=int, default=1)

    parser.add_argument("--rebin", type=int, default=1)
    parser.add_argument("--detd", type=float, default=1)
    parser.add_argument("--lamb", type=float, default=1)
    parser.add_argument("--tag", type=str, default='tag')
    parser.add_argument("--crop-size", type=int, nargs=2, metavar=('NY','NX'), default=[1306, 1093])

    args = parser.parse_args()

    assert args.rebin in [1,2,4,8], 'rebin must be either 1,2,4,8'
    assem_center = [657.61, 538.40]

    if args.tag != '':
        args.tag = '_'+args.tag

    if args.crop_size==[1306, 1093]:
        xstart, xend = [0,1093]
        ystart, yend = [0,1306]
    else:
        xstart, xend = round(assem_center[1] - args.crop_size[1]//2), round(assem_center[1] + args.crop_size[1]//2)
        ystart, yend = round(assem_center[0] - args.crop_size[0]//2), round(assem_center[0] + args.crop_size[0]//2)

    crop_center = [assem_center[0]  - ystart, assem_center[1] - xstart]



   
    MASK_FNAME = './det/mask_hvoff_20250311.h5'



    with h5py.File(MASK_FNAME, 'r') as f:
        mask = f['/entry_1/data_1/mask'][...]

    #assem = np.ones( (1306, 1093) )

    assem = assembleImage(mask)

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


