#!/bin/bash
#SBATCH --job-name=uploadAllas
#SBATCH --output=logs/03out-uploadFBS.txt
#SBATCH --error=logs/03err-uploadFBS.txt
#SBATCH --account=project_2000371
# SBATCH --time=01:00:00 
# SBATCH --mem=10G
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

echo "Now's the time:"
dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt"

#RUN:
python ../python/03-boto3-Allas-upload.py -i /scratch/project_2000371/FBSadjusted/results/adjusted -b FoodBalanceSheets
python ../python/03-boto3-Allas-upload.py -i /scratch/project_2000371/FBSadjusted/results/interpolatedLinear/ -b FoodBalanceSheets
python ../python/03-boto3-Allas-upload.py -i /scratch/project_2000371/FBSadjusted/results/shannon/ -b FoodBalanceSheets
