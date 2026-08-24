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
```

Enter the repo, and set up the virtual environment and activate it.
```
cd dfly-p6933
python -m venv dfly
source dfly/bin/activate
pip install mpi4py
pip install extra_data
pip install ipympl
pip install scikit-image
```

If you want to install the environment for use in jupyter
```
pip install ipykernel
python -m ipykernel install --user --name dfly --display-name "Python (dfly)"
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
cd ..
```

Create a dragonfly reconstruction folder.
```
dragonfly.init -t test
```

Save the hits in a dragonfly readable format.
```
mkdir hits
mpirun -np 16 -- python save_hits.py --run-number 306 --crop-size 256 256 --rebin 1
mpirun -np 16 -- python save_hits.py --run-number 307 --crop-size 256 256 --rebin 1
```

Save a config and detector file to the reconstruction folder we created.
```
python setup_df.py --df-tag test_0001 --hit-tags hits/r0306_cp256_rb1 hits/r0307_cp256-rb1 --detd 214 --lamb 1.26 | bash
```

Run the dragonfly reconstruction.
```
sbatch slurm_dragonfly.sh test_0001
```

Continue the dragonfly reconstruction.
```
sbatch slurm_resume_dragonfly.sh test_0001
```


Install libspimage.
```
git clone https://github.com/YellowSub17/libspimage.git
cd libspimage
mkdir build
cd build
```



This is the magic command to avoid ccmake menu configuration.

```
cmake \
  -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV \
  -DPython3_FIND_VIRTUALENV=FIRST \
  -DPYTHON_EXECUTABLE="$VIRTUAL_ENV/bin/python" \
  -DPYTHON_INCLUDE_PATH="$(python -c 'import sysconfig; print(sysconfig.get_path("include"))')" \
  -DPYTHON_INSTDIR="$(python -c 'import sysconfig; print(sysconfig.get_path("platlib"))')" \
  -DPython3_LIBRARY="" \
  -DPYTHON_LIBRARIES="" \
  -DCMAKE_SHARED_LINKER_FLAGS="-Wl,--undefined" \
  ..
make
make install
```













