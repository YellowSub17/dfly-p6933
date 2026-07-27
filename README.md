# dfly-p6933


## Setup

This is setup is assuming you are working on maxwell.

First, clone this repo and load some module

```
git clone https://github.com/YellowSub17/dfly-p6933
module purge
module load maxwell
module load mpi/openmpi-x86_64
module load cuda/12.6
module load python/3.13
<!--module load exfel-->
<!--module load exfel-python-->
```

Enter the repo, and set up the virtual environment and activate it.
```
cd dfly-p6933
python -m venv dfly
source dfly/bin/activate
pip install mpi4py
pip install extra_data
```



Install dragonfly.
```
git clone https://github.com/YellowSub17/Dragonfly
cd Dragonfly
pip install -e .
mkdir build
cd build
cmake ..
make
rehash
```

Create a dragonfly reconstruction folder.
```
dragonfly.init -t test
```

Save the hits in a dragonfly readable format.
```
mkdir hits
mpirun -np 16 -- python --run-number 306 --crop-size 256 256 --rebin 1
mpirun -np 16 -- python --run-number 307 --crop-size 256 256 --rebin 1
```

Save a config and detector file to the reconstruction folder we created.
```
python setup_df.py --df-tag test_0001 --hit-tags hits/r0306_cp256_rb1 hits/r0307_cp256-rb1 --detd 86.9 --lamb 1.26 | bash
```

Run the dragonfly reconstruction.
```

```





