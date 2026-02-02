#!/bin/bash
#SBATCH --job-name=02-FBSinterpolate
#SBATCH --output=logs/02out-interpolateFBS
#SBATCH --error=logs/02err-interpolateFBS
#SBATCH --account=project_2000371
#SBATCH --time=00:20:00 # takes 11min or 17min 
#SBATCH --mem=10G
#SBATCH --ntasks=1
#SBATCH --partition=small

module load geoconda

#RUN:
python ../python/02-interpolate-missing-values.py -i /scratch/project_2000371/FBSadjusted/results/adjusted -y 2023 -m linear
