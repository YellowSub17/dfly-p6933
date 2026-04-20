

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




if __name__=='__main__':

    parser = argparse.ArgumentParser(description='save_hits.py -- Convert hits from extra-data into h5 files, to be converted to emc files.\nUsage: mpirun -np 16 -- python save_hits.py --rebin 4 249')
    parser.add_argument("run_number", type=int)
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







    proposal = 6933


    mpi_comm = MPI.COMM_WORLD

    mpi_rank = mpi_comm.Get_rank()
    mpi_size = mpi_comm.Get_size()

    if mpi_rank==0:
        os.makedirs(f'./hit_images/r{args.run_number:04}{args.tag}/', exist_ok=True)


    if mpi_rank==0:
        print('opening run')
    run = extra_data.open_run(proposal=proposal, run=args.run_number, parallelize=True)

    if mpi_rank==0:
        print('getting tphi')
    tphi = get_tphi(run, 100)



    worker_tphi = np.array_split(tphi, mpi_size)[mpi_rank]
    geom_fn = "./geom/agipd_p008039_r0014_v16.geom"
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

        assem,_ = ref_geom.position_modules(ans)

        assem = assem[0,0,ystart:yend, xstart:xend]   ## 1266, 1112

        assem_height, assem_width = assem.shape

        rebin_height, rebin_width  = assem_height//args.rebin, assem_width//args.rebin

        assem_rebin = assem.reshape(rebin_height, args.rebin, rebin_width, args.rebin).sum(axis=(1,3))






        with h5py.File(f'./hit_images/r{args.run_number:04}{args.tag}/r{args.run_number:04}{args.tag}_i{int(ind):03}.h5', 'w') as f:
            f['/data'] = assem_rebin
            f['/rebin'] = args.rebin
            f['/crop-size'] = args.crop_size































