
import h5py
import sys

df_tag = sys.argv[1]
mask_h5 = sys.argv[2]






with h5py.File(mask_h5, 'r') as f:
    mask_data = f['/mask'][...]

with h5py.File(f'{df_tag}/data/det.h5', 'a') as f:
    f['/mask'][...] = mask_data
