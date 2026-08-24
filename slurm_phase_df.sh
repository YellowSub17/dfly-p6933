#!/bin/zsh
#SBATCH --partition=allgpu
#SBATCH --time=3-00:00:00 
#SBATCH --job-name="runrecnon" 
#SBATCH -o .slurm-output/job-output-%j
#



source dfly/bin/activate

module load mpi/openmpi-x86_64
module load maxwell
module load cuda



python phase_df.py --df-tag $1 --rec-file ./RECIPE.TXT

