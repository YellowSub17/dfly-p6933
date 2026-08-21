#!/bin/zsh
#SBATCH --partition=upex
#SBATCH --time=3-00:00:00 
#SBATCH --job-name="dragonfly" 
#SBATCH -o .slurm-output/job-output-%j
#

module purge
module load mpi/openmpi-x86_64

source dfly/bin/activate


cd $1

mpirun -np 16 dragonfly.emc -t 8 -c ./config.ini $2


