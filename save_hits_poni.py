

from mpi4py import MPI
import numpy as np
import extra_data
import extra_geom
import h5py
import sys
import os
import argparse


def get_tphi(run, n_brightest=-1):
    det = {
    'agipd': 'SPB_DET_AGIPD1M-1/CORR/*',                         # Main 2d detector
    'hitfinder': 'SPB_DET_AGIPD1M-1/REDU/SPI_HITFINDER:output',  # Flags the hits
    }
    hitscore = run[det['hitfinder'],'data.hitscore'].xarray()
    hitflags = run[det['hitfinder'],'data.hitFlag'].xarray()
    hitpulse = run[det['hitfinder'],'data.pulseId'].xarray()
    trainids = hitscore.coords['trainId'].values
    # Create an xarray with all trainIds and corresponding hitscores the hitfinder flags
    flagged = hitscore*hitflags
    sort_indices = np.argsort(flagged.data)[::-1]
    sorted_hitscore = hitscore.data[sort_indices][:n_brightest]
    sorted_pulseids = hitpulse.data[sort_indices][:n_brightest]
    sorted_trainids = trainids[sort_indices][:n_brightest]
    return np.array([sorted_trainids, sorted_pulseids, sorted_hitscore, np.arange(sorted_trainids.size)]).T




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
    ret_img = np.full((1306, 1093),  0)
    for m_nr, module in enumerate(not_assembled_image):
        trafo = np.rot90(module, axes=(0, 1)) if m_nr<8 else np.rot90(module, axes=(1, 0))
        for t_nr in range(8):
            ref_y, ref_x = det_edges[m_nr, t_nr]
            ret_img[ref_y:ref_y+128, ref_x:ref_x+64] = trafo[:, t_nr*64:(t_nr+1)*64]
    return ret_img


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='save_hits.py -- Convert hits from extra-data into h5 files, to be converted to emc files.')
    parser.add_argument("--run-number", type=int)
    parser.add_argument("--from-curated", type=bool, default=False)
    parser.add_argument("--rebin", type=int, default=1)
    parser.add_argument("--tag", type=str, default='')
    parser.add_argument("--crop-size", type=int, nargs=2, metavar=('NY','NX'), default=[1306, 1093])
    parser.add_argument("--center", type=float, nargs=2, metavar=("CY", "CX"), default=[657.61, 538.40])
    

    ##1306->1304 (-1 top -1 bottom), 1093->1096 (+1 lhs +2 rhs)??




    args = parser.parse_args()


   
    assert args.rebin in [1,2,4,8], 'rebin must be either 1,2,4,8'

    if args.tag != '':
        args.tag = '_'+args.tag

    if args.crop_size==[1306, 1093]:
        xstart, xend = [0,1093]
        ystart, yend = [0,1306]
    else:
        xstart, xend = round(args.center[1] - args.crop_size[1]//2), round(args.center[1] + args.crop_size[1]//2)
        ystart, yend = round(args.center[0] - args.crop_size[0]//2), round(args.center[0] + args.crop_size[0]//2)
    
    

    proposal = 6933


    mpi_comm = MPI.COMM_WORLD

    mpi_rank = mpi_comm.Get_rank()
    mpi_size = mpi_comm.Get_size()
    if mpi_rank==0:
        print(xstart, xend, ystart, yend)

    if mpi_rank==0:
        os.makedirs(f'./hit_images/r{args.run_number:04}{args.tag}/', exist_ok=True)



    if mpi_rank==0:
        print('opening run')
    run = extra_data.open_run(proposal=proposal, run=args.run_number, parallelize=True)

    if not args.from_curated:
        if mpi_rank==0:
            print('getting tphi')
        tphi = get_tphi(run, 100)

    else:
        with h5py.File(f'/gpfs/exfel/u/usr/SPB/202501/p006933/Shared/buchin/spb_dev/curated_data/run{args.run_number:04}_curated.h5', 'r') as curated_h5:
            t = curated_h5['/trainId'][:]
            p = curated_h5['/pulseId'][:]
            h = np.ones(p.shape)*-1
            i = np.arange(p.size)
        tphi = np.array([t, p, h, i]).T






    worker_tphi = np.array_split(tphi, mpi_size)[mpi_rank]
    geom_fn = "./det/agipd_p008039_r0014_v16.geom"
    ref_geom = extra_geom.AGIPD_1MGeometry.from_crystfel_geom(geom_fn)


    for tid, pid, hitscore,ind in worker_tphi:

        if mpi_rank==0:
            print(ind)
        sel_im = run.select('SPB_DET_AGIPD1M-1/CORR/*', "image.data")
        sel_pulseid = run.select('SPB_DET_AGIPD1M-1/CORR/*', "image.pulseId", )
        _, train_data_im = sel_im.train_from_id(tid)
        _, train_data_pulseid = sel_pulseid.train_from_id(tid)

        pulse_index = np.argwhere(train_data_pulseid['SPB_DET_AGIPD1M-1/CORR/2CH0:output']['image.pulseId']==pid)

        stack = extra_data.stack_detector_data(train_data_im, 'image.data', pattern='/CORR/(\\d+)CH')

        ans = stack[pulse_index,:,...]

       
        assem = assembleImage(ans[0,0])
        
        assem = assem[ystart:yend, xstart:xend]   ## 1266, 1112

        assem_height, assem_width = assem.shape

        rebin_height, rebin_width  = assem_height//args.rebin, assem_width//args.rebin
        

        assem_rebin = assem.reshape(rebin_height, args.rebin, rebin_width, args.rebin).sum(axis=(1,3))




        with h5py.File(f'./hit_images/r{args.run_number:04}{args.tag}/r{args.run_number:04}{args.tag}_i{int(ind):03}.h5', 'w') as f:
            f['/data'] = assem_rebin
            f['/rebin'] = args.rebin
            f['/crop-size'] = args.crop_size
            f['/from-curated'] = args.from_curated
            f['/center'] = args.center
            
            
            































