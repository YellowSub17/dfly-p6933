

mpirun -np 16 -- python save_hits.py --run-number 306 --crop-size 512 512 --rebin 2
mpirun -np 16 -- python save_hits.py --run-number 306 --crop-size 256 256 --rebin 1

mpirun -np 16 -- python save_hits.py --run-number 307 --crop-size 512 512 --rebin 2
mpirun -np 16 -- python save_hits.py --run-number 307 --crop-size 256 256 --rebin 1
