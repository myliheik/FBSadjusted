#!/bin/bash
#SBATCH --job-name=01-FBSadjust
#SBATCH --output=logs/01-output_adjustFBS_out.txt
#SBATCH --error=logs/01-output_adjustFBS_err.txt
#SBATCH --account=project_2000371
#SBATCH --time=01:00:00 # 28mins! or 32min
#SBATCH --mem=10G
#SBATCH --ntasks=1
#SBATCH --partition=small

module load geoconda

#RUN:
# for one element only:
#python ../python/adjustOldFBSdataWithNew-fromBulkDownload.py -e 645 -o /scratch/project_2000371/FBSadjusted/results \
#-n /scratch/project_2000371/FBSadjusted/FAObulkdata/FoodBalanceSheets_E_All_Data_Normalized.csv \
#-d /scratch/project_2000371/FBSadjusted/FAObulkdata/FoodBalanceSheetsHistoric_E_All_Data_Normalized.csv

#OR for all elements:

python ../python/01-adjustOldFBSdataWithNew-fromBulkDownload.py -o /scratch/project_2000371/FBSadjusted/results/adjusted \
-n /scratch/project_2000371/FBSadjusted/FAObulkdata/FoodBalanceSheets_E_All_Data_Normalized.csv \
-d /scratch/project_2000371/FBSadjusted/FAObulkdata/FoodBalanceSheetsHistoric_E_All_Data_Normalized.csv


# Elements:
#{'511': 'Total Population - Both sexes', '2510': 'Production Quantity', '2610': 'Import quantity', '2071': 'Stock Variation', '2910': 'Export quantity', '2300': 'Domestic supply quantity', 
#'2520': 'Feed', '2525': 'Seed', '2120': 'Losses', '2130': 'Processed', '2151': 'Other uses (non-food)', '5171': 'Tourist consumption', '5170': 'Residuals', '2141': 'Food', 
#'645': 'Food supply quantity (kg/capita/yr)', '664': 'Food supply (kcal/capita/day)', '661': 'Food supply (kcal)', '674': 'Protein supply quantity (g/capita/day)', '671': 'Protein supply quantity (t)', 
#'684': 'Fat supply quantity (g/capita/day)', '681': 'Fat supply quantity (t)'}
