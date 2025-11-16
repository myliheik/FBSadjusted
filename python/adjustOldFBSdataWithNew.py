"""
2025-11-11 MY

RUN:
python adjustOldFBSdataWithNew.py -e 645 -o /Users/myliheik/Documents/myPython/FBSadjusted/results

OR for all elements:

python adjustOldFBSdataWithNew.py -o /Users/myliheik/Documents/myPython/FBSadjusted/results

"""

import faostat
import pandas as pd

import warnings
import re
import os.path
from pathlib import Path
import argparse
import textwrap


# ignore warnings
warnings.filterwarnings('ignore')

# take all elements, areas and items in Food Balance Sheets:
# List/dictionary of elements
elementDict = faostat.get_par('FBS', 'element')
elements = list(elementDict.keys())
elementDictReverse = dict(zip(elementDict.values(), elementDict.keys()))

# List/dictionary of countries/regions:
areaDict = faostat.get_par('FBS', 'area')
areas = list(areaDict.keys())#[55:57] # Finland and France

# List/dictionary of items
myItemsDict = faostat.get_par('FBS', 'item')
myItemsKeys = list(myItemsDict.keys())
# Let's remove 'Grand Total > (List)': '2901>' types of items:
for item in myItemsKeys:
    if '>' in item:
        print(item)
        myItemsDict.pop(item, None) 
        



##### FUNCTIONS:
def correctionBias(myElement, itemsDict, out_dir_path):
    # Initiate a list for results:
    results = []
    fishyResults = [] # collect fishy results to check out later
    
    # Loop all countries/regions:
    for myCountry in areas:
        # Loop all items:
        for myItem in myItemsKeys:
            myItemCode = itemsDict.get(myItem)
            # Check if item is found in the database:
            if myItemCode:
                pass                    
            else:
                continue # go to next item
            
            # Prepare database call, parameters:
            mypars = {'element': [elementDict.get(myElement)],'area': areaDict.get(myCountry), 'item': myItemCode}

            #mycoding = {'area': 'ISO3'}
            mycoding = {'area': 'FAO'}
            #print(mypars)
            # Fetch data from the new FBS:
            newdata = faostat.get_data_df('FBS', pars=mypars, coding=mycoding, strval=False)

            if newdata.empty:
                #print(f'No FBS data found for {myItem} in {myCountry}.')
                continue

            else:

                newdata['Domain'] = 'New FBS'
                #print(f'New data shape: {newdata.shape}, should be 14.')
                # Fetch data from the historical (old) FBS:
                olddata = faostat.get_data_df('FBSH', pars=mypars, coding=mycoding, strval=False)
                if olddata.empty:
                    #print(f'No FBSH data found for {myItem} in {myCountry}.')
                    continue
                else:
                    olddata['Domain'] = 'Old FBS'
                    #print(f'Old data shape: {olddata.shape}, should be 53.')
                    # Merge old and new data:
                    data = pd.concat([olddata, newdata], axis = 0).reset_index()
                    #print(f'Merged data shape: {data.shape}, should be 67.')
                    # Correction:
                    # Take duplicated years into a subset (should be 2010-2013):
                    correctionSubset = data[data.Year.duplicated(keep = False)]   
                    #print(f'Subset data shape: {correctionSubset.shape}, should be 8.')

                    if len(correctionSubset) < 8:
                        print(f'Less than 4 years is not enough to make the correction. We skip item {myItem} of {myCountry}')
                        continue
                    else:
                        pass
                    

                    # Take the difference of each year and their mean:
                    MeanDiffBias = round(correctionSubset[['Year', 'Value']].groupby('Year').diff().mean()[0], 1)
                    # What is the scale of correction related to the original values (their mean):
                    if not correctionSubset['Value'].mean() == 0:
                        MeanDiffBiasPerc = round(100*MeanDiffBias/correctionSubset['Value'].mean(),1)
                    else:
                        MeanDiffBiasPerc = 0
                    #print(f'Correction bias: {round(MeanDiffBias[0], 1)}')
                    #print(f'Correction bias: {MeanDiffBias}')
                    if pd.isna(MeanDiffBiasPerc):
                        print(f'MeanDiffBiasPerc is {MeanDiffBiasPerc}%')
                        print(mypars)
                        exit()
                    else:
                        pass

                    # Subset the old data and add the bias correction:
                    dataMeanDiffBias = data[data['Domain'] == 'Old FBS'].drop(columns = ['Value', 'Domain'])
                    #print(f'Subset2 data shape: {dataMeanDiffBias.shape}, should be 53.')
                    dataMeanDiffBias['Value'] = round(data['Value'][data['Domain'] == 'Old FBS'] + MeanDiffBias, 2)
                    # Exclude 2010-2013 (these years will have the new data to use):
                    dataMeanDiffBias = dataMeanDiffBias[~dataMeanDiffBias['Year'].isin(['2010', '2011', '2012', '2013'])]

                    # Combine new data (2010-) with the bias corrected old data (up to 2009):
                    AdjustedFinal0 = data[data['Domain'] == 'New FBS'].drop(columns = ['Domain'])
                    AdjustedFinal = pd.concat([AdjustedFinal0, dataMeanDiffBias])
                    # Replace below zero values with 0.001
                    AdjustedFinal['Value'] = AdjustedFinal['Value'].mask(AdjustedFinal['Value'] < 0, 0.001)

                    AdjustedFinal['Domain'] = 'BiasCorrectedAdjusted'
                    AdjustedFinal['MeanDiffBias'] = MeanDiffBias
                    AdjustedFinal['MeanDiffBiasPerc'] = MeanDiffBiasPerc
                    data['MeanDiffBias'] = None
                    data['MeanDiffBiasPerc'] = None               

                    #print(f'AdjustedFinal data shape: {AdjustedFinal.shape}, should be 63.')
                    #print(f'Data shape: {data.shape}, should be 67.')

                    data2 = pd.concat([data, AdjustedFinal])

                    if data2.shape[0] > 130: # less years is ok, but more reveals duplicates or other fishy issues!
                        print(f'Something is wrong! The number of rows per Area+Item is {data2.shape[0]} and it should be 130!')
                        fishyResults.append(data2)
                        exit()
                    else:                    
                        results.append(data2)

                    #print('Done.')

    df = pd.concat(results, axis = 0, ignore_index = True).drop(columns = ['index'])
    print(f'Results length: {len(results)}')
    print(f'Saving results in {out_dir_path}')
    df.to_csv(out_dir_path, index = False)
    
    if fishyResults:
        dfFishy = pd.concat(fishyResults, axis = 0, ignore_index = True).drop(columns = ['index'])
        out_dir_path22 = os.path.join(os.path.dirname(out_dir_path), 'fishy' + itemsDict.get(myItem) + '.csv')
        print(f'Fishy results length: {len(fishyResults)}')
        print(f'Saving fishy results in {out_dir_path22}')
        dfFishy.to_csv(out_dir_path22, index = False)
    
                   

    return None

# HERE STARTS MAIN:

def main(args):  
    try:
        if not args.outputpath:
            raise Exception('Missing output dir argument. Try --help .')

        print(f'\n\nadjustOldFBSdataWithNew.py')
        
        print("These are the elements in FAO's Food balance sheets:")
                                  
        print(elementDictReverse)

        myElement = args.element
                          
        print(f'\n Files will be saved in {args.outputpath}')
        out_dir_path = args.outputpath
        # directory for results:
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)
        
        # if the user gives the Element:
        if myElement:            
            myElement2 = elementDictReverse.get(myElement)
            print(f'You chose to fetch only {myElement}. That is {myElement2}')
            cleanString = re.sub(r'\W+','-', myElement2)
            out_dir_path2 = os.path.join(out_dir_path, cleanString + '.csv')
            correctionBias(myElement2, myItemsDict, out_dir_path2)           
            
        else:
            # Loop all elements:
            print('We fetch all the elements')
            for myElement in elements:
                print(myElement)
                cleanString = re.sub(r'\W+','-', myElement)
                out_dir_path2 = os.path.join(out_dir_path, cleanString + '.csv')
                correctionBias(myElement, myItemsDict, out_dir_path2)                
                
        print('Done.')

    except Exception as e:
        print('\n\nUnable to read input or write out results. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))
    
    parser.add_argument('-e', '--element',
                        type=str,
                        help='Give the numeric code for the Element. Fetch only the given Element from the FAO database. E.g. 645 for "Food supply quantity (kg/capita/yr)".',
                        default=None)
    parser.add_argument('-o', '--outputpath',
                        type=str,
                        help='Path to the directory where the corrected food balance sheets are saved.',
                        default='.')

    args = parser.parse_args()
    main(args)
