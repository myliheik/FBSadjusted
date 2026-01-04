"""
2025-11-02 MY

RUN for all files in directory:

python 02-interpolate-missing-values.py -i /Users/myliheik/Documents/myPython/FBSadjusted/results/adjusted -y 2023 -m linear

WHERE:
latestYear: the latest year in the data, is found in the filename, e.g. 2023
method:     method for interpolation, e.g. linear

"""

import pandas as pd

import warnings
import re
import os.path
from pathlib import Path
import argparse
import textwrap
import glob


# ignore warnings
warnings.filterwarnings('ignore')

##### FUNCTIONS:
def interpolation(df, myElement, areas, filepath, elementDict, areaDict, interpolationMethod):
    # Initiate a list for results:
    results = []
    i = 0
    # Loop all countries/regions:
    for myCountry in areas:
        # Slice by area and element:
        df2 = df[(df['Area Code'] == myCountry) & (df['Element Code'] == myElement)]        
        
        # This should never happen:
        if df2.empty: # this never happens!
            print(f'Element {elementDict.get(myElement)} ({myElement}) was not found for country {areaDict.get(myCountry)} ({myCountry}) in the data.')
            i = i + 1
            continue
        else:
            pass
        
        
        # Search items of the data:
        items = df2['Item Code'].unique()

        # Loop all items:
        for myItem in items:
            data = df2[df2['Item Code'] == myItem]
            
            # If the data is bias corrected, we take that:
            data2 = data[data['Domain'] == 'BiasCorrectedAdjusted']
            # If the data do not have correction, 
            # then there was no overlapping years
            # and we will work with the data from the new and old method (notAdjusted.csvs)
            if data2.empty: # only notAdjusted data for this country and item
                data3 = data.copy()
            else: # BiasCorrectedAdjusted data for this country and item
                data3 = data2.copy()
                        
            ############ Interpolation:
            # if there are some years missing, do interpolation:
            missing = set(range(data3['Year'].min(), data3['Year'].max())) - set(data3['Year'])
            if len(missing) > 0:
                #print(f'Missing years: {missing}')
                data00 = pd.concat([data3, pd.DataFrame({'Year': list(missing), 'Domain': 'Interpolated', 'interpolationMethod': interpolationMethod.title()})], axis = 0, ignore_index = True)
                data01 = data00.assign(Time = pd.to_datetime(data00['Year'], format = '%Y'))
                data011 = data01.set_index('Time', inplace = False).sort_index()
                data44 = data011.assign(NAsInterpolated = data011['Value'].interpolate(method = interpolationMethod))
                # add metadata:
                # with dictionary:
                metaDict = dict(data44.iloc[0][['Area Code', 'Area', 'Item Code', 'Item', 'Element Code', 'Element', 'Unit']])
                #metaDict.update({'interpolationMethod': interpolationMethod.title()}) # not for all 
                data4 = data44.fillna(metaDict)

            else: # no need for interpolation, we just add new variables NAsInterpolated, interpolationMethod and Time
                data4 = data3.assign(NAsInterpolated = data3['Value'], interpolationMethod = None, Time = pd.to_datetime(data3['Year'], format = '%Y'))
                data4.set_index('Time', inplace = True)
                

            results.append(data4)
        
            
        
    if results:
        dfResults = pd.concat(results, axis = 0, ignore_index = True)#.drop(columns = ['index'])

        print(f'Cases with chaos (missing country): {i}')
        print(f'Results length: {len(results)}')
        print(f'Saving results in {filepath}\n')
        dfResults.to_csv(filepath, index = False)
        
    else:
        print(f'No data on element {elementDict.get(myElement)} ({myElement}).')
    return None



# HERE STARTS MAIN:

def main(args):  
    try:
        if not args.inputpath:
            raise Exception('Missing output dir argument. Try --help .')

        print(f'\n\n02-interpolate-missing-values.py\n\n')

        path = Path(args.inputpath)
        #if args.interpolationMethod == 'linear':
        #    newdirectory = 'interpolated'
        #else:
        newdirectory = 'interpolated' + args.interpolationMethod.title()
            
        out_dir_path = os.path.join(path.parent.absolute(), newdirectory) 
        
        #print(f'\nFiles will be saved in {out_dir_path}')
        # directory for results:
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)

        
        fps = glob.glob(args.inputpath + '/*' + args.latestYear + '*.csv')
        for fp in fps:
            filebase = os.path.basename(fp)
            filepath = os.path.join(out_dir_path, filebase)
            
            
            if not 'notAdjusted' in fp:
                print(f'Reading {fp}')
                df = pd.read_csv(fp)
                #print(df['Domain'].unique())
                # read notAdjusted pair of the data:
                fpnotAdjusted = Path(fp.replace('.csv', '-notAdjusted.csv'))
                if fpnotAdjusted.is_file():
                    print(f'Reading {fpnotAdjusted}')
                    dfnotAdjusted = pd.read_csv(fpnotAdjusted)
                    #print(dfnotAdjusted['Domain'].unique())
                    # join adjusted and not Adjusted data:
                    data0 = pd.concat([df, dfnotAdjusted], axis = 0, ignore_index = True).reset_index()
                    if not (len(dfnotAdjusted) + len(df)) == len(data0):
                        print(f'Something is wrong, data not merged properly.')
                        break

                else:
                    print(f'No notAdjusted data in {fpnotAdjusted}. We only use {fp}\n')
                    data0 = df
                
                areas = data0['Area Code'].unique()
                if len(data0['Element Code'].unique()) == 1:
                    myElement = data0['Element Code'][0] # should be one
                else: 
                    print(f'Data contains multiple elements. Something is wrong. Existing.')
                
                # make a dictionary out of Element Code and Element:
                elementDict0 = data0[['Element Code', 'Element']].drop_duplicates()
                elementDict = dict(zip(elementDict0['Element Code'], elementDict0['Element']))
                
                # make a dictionary out of Area Code and Area:
                areaDict0 = data0[['Area Code', 'Area']].drop_duplicates()
                areaDict = dict(zip(areaDict0['Area Code'], areaDict0['Area']))
                #print(myElement, elementDict)
                interpolation(data0, myElement, areas, filepath, elementDict, areaDict, args.interpolationMethod)
                #break
                    
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
    parser.add_argument('-m', '--interpolationMethod',
                        type=str,
                        help='Method to fill NaN values using interpolation. E.g. linear, nearest, zero. Default linear. Check pandas.DataFrame.interpolate for more information.',
                        default = 'linear'
                        )    
    parser.add_argument('-y', '--latestYear',
                        type=str,
                        help='The latest year in the data, should be found in the filename.',
                        default = 2023)
    parser.add_argument('-i', '--inputpath',
                        type=str,
                        help='Path to the directory where the adjusted food balance sheets were saved.',
                        default='.')

    args = parser.parse_args()
    main(args)
