"""
2025-11-16 MY

RUN for one element:
python adjustOldFBSdataWithNew-fromBulkDownload.py -e 645 -o /Users/myliheik/Documents/myPython/FBSadjusted/results \
-n /Users/myliheik/Documents/myPython/FBSadjusted/data/FoodBalanceSheets_E_All_Data_Normalized/FoodBalanceSheets_E_All_Data_Normalized.csv \
-h /Users/myliheik/Documents/myPython/FBSadjusted/data/FoodBalanceSheetsHistoric_E_All_Data_Normalized/FoodBalanceSheetsHistoric_E_All_Data_Normalized.csv

OR for all elements:

python adjustOldFBSdataWithNew-fromBulkDownload.py -o /Users/myliheik/Documents/myPython/FBSadjusted/results \
-n /Users/myliheik/Documents/myPython/FBSadjusted/data/FoodBalanceSheets_E_All_Data_Normalized/FoodBalanceSheets_E_All_Data_Normalized.csv \
-h /Users/myliheik/Documents/myPython/FBSadjusted/data/FoodBalanceSheetsHistoric_E_All_Data_Normalized/FoodBalanceSheetsHistoric_E_All_Data_Normalized.csv

"""

import pandas as pd

import warnings
import re
import os.path
from pathlib import Path
import argparse
import textwrap


# ignore warnings
warnings.filterwarnings('ignore')

##### FUNCTIONS:

def readData(filepath):
    df = pd.read_csv(filepath)
    areas = df['Area Code'].unique()
    elements = df['Element Code'].unique()

    return df, elements, areas

def correctionBias(olddata, newdata, myElement, areas, out_dir_path, elementDict, areaDict):
    # Initiate a list for results:
    results = []
    fishyResults = [] # collect fishy results to check out later
    i = 0
    
    newdata['Domain'] = 'New FBS'
    olddata['Domain'] = 'Old FBS'
    
    # Loop all countries/regions:
    for myCountry in areas:
        # Slice by area and element:
        newdata2 = newdata[(newdata['Area Code'] == myCountry) & (newdata['Element Code'] == myElement)]        
        olddata2 = olddata[(olddata['Area Code'] == myCountry) & (olddata['Element Code'] == myElement)]      

        if newdata2.empty:
            print(f'Element {elementDict.get(myElement)} ({myElement}) was not found for country {areaDict.get(myCountry)} ({myCountry}) in the new data (2010-).')
            continue
        else:
            pass
        
        # Sometimes an element is not found in the old data...
        # Test:
        if olddata2.empty:
            print(f'Element {elementDict.get(myElement)} ({myElement}) was not found for country {areaDict.get(myCountry)} ({myCountry}) in the old data (-2013).')
            continue
        else:
            pass
        
        
        # Merge old and new data:
        data0 = pd.concat([olddata2, newdata2], axis = 0).reset_index()
        
        # Search items of the newdata:
        items = newdata2['Item Code'].unique()

        # Loop all items:
        for myItem in items:

            data = data0[data0['Item Code'] == myItem]

            # Correction:
            # Take duplicated years into a subset (should be 2010-2013):
            correctionSubset = data[data.Year.duplicated(keep = False)]   
            #print(correctionSubset)
            
            #print(f'Subset data shape: {correctionSubset.shape}, should be 8.')

            if len(correctionSubset) < 8:
                #print(f'Less than 4 years is not enough to make the correction. We skip item {myItem} of {myCountry}')
                i = i + 1
                fishyResults.append(data)
                continue
            else:
                pass


            # Take the difference of each year and their mean:
            MeanDiffBias = correctionSubset[['Year', 'Value']].groupby('Year').diff().mean()[0]
            # What is the scale of correction related to the original values (their mean):
            if not correctionSubset['Value'].mean() == 0:
                MeanDiffBiasPerc = round(100*MeanDiffBias/correctionSubset['Value'].mean(), 1)
            else:
                MeanDiffBiasPerc = 0
            #print(f'Correction bias: {MeanDiffBias}')
            if pd.isna(MeanDiffBiasPerc):
                print(f'MeanDiffBiasPerc is {MeanDiffBiasPerc}%')
                print('Exiting now.')
                exit()
            else:
                pass

            # Subset the old data
            # Exclude 2010-2013 (these years will have the new data to use):
            pre2010data = data[(data['Domain'] == 'Old FBS') & (data['Year'] < 2010)]
            dataMeanDiffBias = pre2010data.drop(columns = ['Value', 'Domain'])
            #print(f'Subset2 data shape: {dataMeanDiffBias.shape}, should be 49.')

            # and add the bias correction:
            dataMeanDiffBias['Value'] = round(pre2010data['Value'] + MeanDiffBias, 2) # should it rounded by 3?
            
            #print(MeanDiffBias)
            #print(dataMeanDiffBias)
            
            # Combine new data (2010-) with the bias corrected old data (up to 2009):
            AdjustedFinal0 = data[data['Domain'] == 'New FBS'].drop(columns = ['Domain'])
            AdjustedFinal = pd.concat([AdjustedFinal0, dataMeanDiffBias])
            # Replace below zero values with 0:
            AdjustedFinal['Value'] = AdjustedFinal['Value'].mask(AdjustedFinal['Value'] < 0, 0)

            AdjustedFinal['Domain'] = 'BiasCorrectedAdjusted'
            AdjustedFinal['MeanDiffBias'] = round(MeanDiffBias, 1)
            AdjustedFinal['MeanDiffBiasPerc'] = MeanDiffBiasPerc
            data['MeanDiffBias'] = None
            data['MeanDiffBiasPerc'] = None               

            #print(f'AdjustedFinal data shape: {AdjustedFinal.shape}, should be 63.')
            #print(f'Data shape: {data.shape}, should be 67.')

            data2 = pd.concat([data, AdjustedFinal])
                 
            results.append(data2)
            
            
    if results:
        df = pd.concat(results, axis = 0, ignore_index = True).drop(columns = ['index'])
        print(f'Results length: {len(results)}')
        print(f'Saving results in {out_dir_path}')
        df.to_csv(out_dir_path, index = False)
        print(f'Cases that did not have 4 years of overlapping years and were omitted: {i}')
        if i > 0:
            dfFishy = pd.concat(fishyResults, axis = 0, ignore_index = True).drop(columns = ['index'])
            out_dir_pathFishy = out_dir_path.replace('.csv', '-notAdjusted.csv')
            print(f'Saving results in {out_dir_pathFishy}')
            dfFishy.to_csv(out_dir_pathFishy, index = False)
        else:
            pass
    else:
        print(f'No data on element {elementDict.get(myElement)} ({myElement}).')
    return None

# HERE STARTS MAIN:

def main(args):  
    try:
        if not args.outputpath:
            raise Exception('Missing output dir argument. Try --help .')

        print(f'\n\nadjustOldFBSdataWithNew-fromBulkDownload.py')
        

        myElement = args.element
                          
        print(f'\n Files will be saved in {args.outputpath}')
        out_dir_path = args.outputpath
        # directory for results:
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)

        dfold = pd.read_csv(args.fpold, encoding = 'latin-1') # There was a problem in reading, adding encoding here fixed the problem
        dfnew, elements, areas = readData(args.fpnew)       
        
        # make a dictionary out of Element Code and Element:
        elementDict0 = dfnew[['Element Code', 'Element']].drop_duplicates()
        elementDict = dict(zip(elementDict0['Element Code'], elementDict0['Element']))

        # make a dictionary out of Area Code and Area:
        areaDict0 = dfnew[['Area Code', 'Area']].drop_duplicates()
        areaDict = dict(zip(areaDict0['Area Code'], areaDict0['Area']))
        
        print("These are the elements in FAO's Food balance sheets:")
                                  
        print(elementDict)

        
        # if the user gives the Element:
        if myElement:            
            if myElement in dfold['Element Code'].values:
                myElement2 = elementDict.get(myElement)
                print(f'You chose to fetch only {myElement}. That is {myElement2}')
                cleanString = re.sub(r'\W+','-', myElement2)
                out_dir_path2 = os.path.join(out_dir_path, cleanString + '.csv').replace('-.csv', '.csv')
                correctionBias(dfold, dfnew, myElement, areas, out_dir_path2, elementDict, areaDict)
            else:
                print(f'No data on element {elementDict.get(myElement)} ({myElement}).')
                            
        else:
            # Loop all elements:
            print('We fetch all the elements')
            for myElement in elements:
                if myElement in dfold['Element Code'].values:
                    myElement2 = elementDict.get(myElement)
                    print(f'\n\n{myElement2}')
                    cleanString = re.sub(r'\W+','-', myElement2)
                    out_dir_path2 = os.path.join(out_dir_path, cleanString + '.csv').replace('-.csv', '.csv')
                    correctionBias(dfold, dfnew, myElement, areas, out_dir_path2, elementDict, areaDict)
                else:
                    print(f'No data on element {elementDict.get(myElement)} ({myElement}).')
                
        print('Done.')

    except Exception as e:
        print('\n\nUnable to read input or write out results. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))
    parser.add_argument('-n', '--fpnew',
                        type=str,
                        help='Path to the directory where the new food balance sheet data are saved.',
                        )
    parser.add_argument('-d', '--fpold',
                        type=str,
                        help='Path to the directory where the historical food balance sheet data are saved.',
                        )    
    parser.add_argument('-e', '--element',
                        type=int,
                        help='Give the numeric code for the Element. Fetch only the given Element from the dataset. E.g. 645 for "Food supply quantity (kg/capita/yr)".',
                        default=None)
    parser.add_argument('-o', '--outputpath',
                        type=str,
                        help='Path to the directory where the corrected food balance sheets are saved.',
                        default='.')

    args = parser.parse_args()
    main(args)
