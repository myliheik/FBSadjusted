#!/bin/bash
#SBATCH --job-name=05-shannon
#SBATCH --output=logs/05out-shannon.txt
#SBATCH --error=logs/05err-shannon.txt
#SBATCH --account=project_2000371
#SBATCH --time=01:00:00  # takes 11mins
# SBATCH --mem=10G
#SBATCH --ntasks=1
#SBATCH --partition=small

module load geoconda

echo "Now's the time:"
dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt"

#RUN:

python ../python/05-calculateShannonIndex.py -i /scratch/project_2000371/FBSadjusted/results/interpolatedLinear -y 2023 \
-m /projappl/project_2000371/FBSadjusted/data/UNSD-countries-regions.csv
