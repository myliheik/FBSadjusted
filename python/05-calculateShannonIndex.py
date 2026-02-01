"""
2026-01-07 Maria Yli-Heikkilä
2026-01-30 MY Area code (M49) recoded into ISO alpha-3, when saving the results 

RUN for all files in directory:

Calculate time series of Shannon index (diversity) that is calculated over all (except excluded) items of a country
after the rolling mean is applied.

python 05-calculateShannonIndex.py -i /Users/myliheik/Documents/myPython/FBSadjusted/results/interpolatedLinear -y 2023 \
-m /Users/myliheik/Documents/myPython/FBSadjusted/data/UNSD-countries-regions.csv

WHERE:
i: input directory
y: the latest year in the data, is found in the filename, e.g. 2023
m: metadata dictionary

"""

import pandas as pd
import faostat
import warnings
import numpy as np
import pickle
import re
import os.path
from pathlib import Path
import argparse
import textwrap
import glob


# ignore warnings
warnings.filterwarnings('ignore')

# These items are excluded:
drop = ('Alcoholic Beverages', 'Beverages, Alcoholic', 'Wine', 'Beer', 'Cloves', 'Spices', 'Pepper', 'Pimento',
       'Spices, Other', 'Coffee and products', 'Cocoa Beans and products', 'Tea (including mate)')

##### FUNCTIONS:

# Applied for a country:
def rollingMeanForOneItem(df, myElement, myItemCode):
    # Subset df:
    df2 = df[(df['Element Code'] == myElement) & (df['Item Code'] == myItemCode)]
    df2 = df2.assign(Time = pd.to_datetime(df2.Year, format='%Y'))
    if df2['Year'].duplicated().any():
        print('Duplicated years!')
    #if len(df2) is not timeSeriesLength:
    #    #print(f'Time series lenght is {len(df2)} and it should be {timeSeriesLength}')
    #    pass
    df3 = df2[['Time', 'NAsInterpolated']]
    df4 = df3.set_index('Time').sort_index()
    # moving average:
    df4[myItemCode] = df4['NAsInterpolated'].rolling(3).mean()
    return df4[myItemCode]




####


def calculateShannon(df, myElement, myM49codes):
    myCountryShannon = []
    myCountries = []

    # for each country:
    for myCountryM49 in myM49codes:
        allItems = []
        # reformat M49 code as M49_xxx:
        myCountryM49str = 'M49_' + str(int(myCountryM49.lstrip("'")))

        #print(f'\nM49: {myCountryM49}')
        #print(f'M49 for a column name: {myCountryM49str}')           
        
        # subset country:
        df2 = df[(df['Area Code (M49)'] == myCountryM49)]

        # take all items:
        myItemDict = df2.set_index('Item').to_dict()['Item Code']
        # drop items that we dont need (spices, non-food, alcohol):
        newItemDict = {k: v for k, v in myItemDict.items() if k not in drop}

        # iterate each item:
        for myItem, myItemCode in newItemDict.items():
            #print(myItem)
            allItems.append(rollingMeanForOneItem(df2, myElement, myItemCode))

        myCountrydf = pd.concat(allItems, axis = 1)
        # row sums:
        myCountrydf['AnnualTotal'] = myCountrydf.sum(axis = 1)
        # share of each item from the Annual Total:
        myCountryShares = myCountrydf.div(myCountrydf['AnnualTotal'], axis=0)    
        # each item ** itsef:
        myCountryPowers = myCountryShares.pow(myCountryShares.values)
        myCountryProduct = myCountryPowers.prod(min_count=1, axis = 1) # at least one item value per year
        Shannon = np.log(1/myCountryProduct)
        myCountryShannon.append(Shannon)
        myCountries.append(myCountryM49str)
        
    
    dfShannon = pd.concat(myCountryShannon, axis = 1)
    dfShannon.columns = myCountries
    
    return dfShannon

# HERE STARTS MAIN:

def main(args):  
    try:
        if not args.inputpath:
            raise Exception('Missing input directory argument. Try --help .')

        print(f'\n\n05-calculateShannonIndex.py\n\n')

        path = Path(args.inputpath)

        newdirectory = 'shannon'
            
        out_dir_path = os.path.join(path.parent.absolute(), newdirectory) 
        
        #print(f'\nFiles will be saved in {out_dir_path}')
        # directory for results:
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)

        latestYear = args.latestYear

        timeSeriesLength = int(latestYear)-1961+1
        print(f'Time series lenght is {timeSeriesLength} ({latestYear} - 1961 + 1)')

        # Read metadata dictionaries (includes country/region/group name, M49, ISO A3):
        dfmeta = pd.read_csv(args.M49, sep = ';')
        
        fps = glob.glob(os.path.join(args.inputpath, '*' + latestYear + '.csv'))
        for fp in fps:
            filebase = os.path.basename(fp)
            filepath = os.path.join(out_dir_path, filebase)            
            
            if Path(fp).is_file():
                print(f'Reading {fp}')   
                df = pd.read_csv(fp)
                if len(df['Element Code'].unique()) == 1:
                    myElement = df['Element Code'][0] # should be one
                else: 
                    print(f'Data contains multiple elements. Something is wrong. Exiting.')
                
                # prepare unique M49 codes to loop:
                myM49codes = df['Area Code (M49)'].dropna().unique()
                
                dfShannon = calculateShannon(df, myElement, myM49codes)
                
                # add metadata to the table:
                dfShannon2 = dfShannon.transpose().reset_index()
                dfShannon2['M49 Code'] = dfShannon2['index'].str.replace('M49_', '').astype(int)
                dfShannon3 = dfShannon2.merge(dfmeta, how = 'left', on = "M49 Code").drop(columns = 'index').rename_axis('index')
                
                # Save to file:
                print(f'Saving results in {filepath}\n')
                dfShannon3.to_csv(filepath, index = False)
                
            else:
                continue
        
        print('Done.')

    except Exception as e:
        print('\n\nUnable to read input or write out results. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))
 
    parser.add_argument('-y', '--latestYear',
                        type=str,
                        help='The latest year in the data, should be found in the filename.',
                        default = 2023)
    parser.add_argument('-i', '--inputpath',
                        type=str,
                        help='Path to the directory where the interpolated food balance sheets were saved.',
                        default='.')
    parser.add_argument('-m', '--M49',
                        type=str,
                        help='Path to the directory where the metadata with region/country and ISO-alpha3 codes are saved.',
                        default='.')
    
    args = parser.parse_args()
    main(args)

