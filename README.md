# dfly-p6933


```
python make_det.py --crop-size 512 512 --tag cp512 --rebin 1 --detd 86.9 --lamb 1.258 | bash
```

```
mpirun -np 16 --python save_hits.py --crop-size 512 512 --tag cp512 306
```

```
dragonfly.init
```

```
python prep_recon.py --hit-tags r0306_cp512 r0307_cp512 --recon-dir recon_0001 --config-ini ./det/config_cp512.ini | bash
```

