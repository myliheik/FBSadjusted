"""
2025-11-11 MY

RUN:
python adjustOldFBSdataWithNew.py

"""
myElement = 'Food supply quantity (kg/capita/yr)'

import faostat
import pandas as pd
import warnings

# ignore warnings
warnings.filterwarnings('ignore')

# take all elements, areas and items in Food Balance Sheets:
# List/dictionary of elements
elementDict = faostat.get_par('FBS', 'element')
elements = list(elementDict.keys())

# List/dictionary of countries/regions:
areaDict = faostat.get_par('FBS', 'area')
areas = list(areaDict.keys())

# List/dictionary of items
myItemsDict = faostat.get_par('FBS', 'item')
myItemsKeys = list(myItemsDict.keys())

# List/dictionary of aggregated items:
myItemsAggDict = faostat.get_par('FBS', 'itemsagg')
myItemsAggKeys = list(myItemsDict.keys())

##### FUNCTIONS:
def correctionBias(myElement):
    # Initiate a list for results:
    results = []
    # Loop all countries/regions:
    for mycountry in areas:
        # Loop all items:
        for myItem in myItemsKeys:
            print(myItem)
            print(mycountry)
            print(elementDict.get(myElement))
            print(myItemsDict.get(myItem))
            
            # Prepare database call, parameteres:
            mypars = {'element': [elementDict.get(myElement)],'area': areaDict.get(mycountry), 'item': myItemsDict.get(myItem)}

            #mycoding = {'area': 'ISO3'}
            mycoding = {'area': 'FAO'}
            #print(mypars)
            # Fetch data from the new FBS:
            newdata = faostat.get_data_df('FBS', pars=mypars, coding=mycoding, strval=False)
            if newdata.empty:
                print(f'No FBS data found for {myItem} in {mycountry}.')
                continue

            else:

                newdata['Domain'] = 'New FBS'
                
                # Fetch data from the historical (old) FBS:
                olddata = faostat.get_data_df('FBSH', pars=mypars, coding=mycoding, strval=False)
                if olddata.empty:
                    print(f'No FBSH data found for {myItem} in {mycountry}.')
                    continue
                else:
                    olddata['Domain'] = 'Old FBS'

                    # Merge old and new data:
                    data = pd.concat([olddata, newdata], axis = 0).reset_index()
                    data.rename(columns = {'Value': myItem}, inplace = True)
                    data['Country'] = mycountry
                    data['Time'] = pd.to_datetime(data.Year, format='%Y')

                    # Correction:
                    # Take duplicated years into a subset (should be 2010-2013):
                    correctionSubset = data[data.Year.duplicated(keep = False)]    
                    # Take the difference of each year and their mean:
                    MeanDiffBias = correctionSubset[['Year', myItem]].groupby('Year').diff().mean()
                    # What is the scale of correction related to the original values (their mean):
                    MeanDiffBiasPros = round(100*MeanDiffBias[0]/correctionSubset[myItem].mean(),1)
                    #print(f'Correction bias: {round(MeanDiffBias[0], 1)}')
                    #print(f'{round(100*MeanDiffBias[0]/correctionSubset[myItem].mean(),1)}%')
                    
                    # Subset the Old data and add the bias correction:
                    dataMeanDiffBias = data[data['Domain'] == 'Old FBS'][['Year', 'Time']]
                    dataMeanDiffBias[myItem] = data[myItem][data['Domain'] == 'Old FBS'] + MeanDiffBias[0]
                    # Exclude 2010-2013 (these years will have the new data to use):
                    dataMeanDiffBias = dataMeanDiffBias[~dataMeanDiffBias['Year'].isin(['2010', '2011', '2012', '2013'])]
                    dataMeanDiffBias['Country'] = mycountry
                    dataMeanDiffBias['Domain'] = 'MeanDiffBiasCorrected'
                    #print(dataMeanDiffBias)

                    # Combine new data (2010-) with the bias corrected old data (up to 2009):
                    AdjustedFinal0 = data[data['Domain'] == 'New FBS'][['Year', 'Time']]
                    AdjustedFinal0[myElement] = data[myElement][data['Domain'] == 'New FBS']
                    AdjustedFinal0['Country'] = mycountry
                    AdjustedFinal = pd.concat([AdjustedFinal0, dataMeanDiffBias])
                    # Replace below zero values with 0.001
                    AdjustedFinal[myElement] = AdjustedFinal[myElement].mask(AdjustedFinal[myElement] < 0, 0.001)

                    AdjustedFinal['Domain'] = 'BiasCorrectedAdjusted'
                    
                    # no need for this:
                    dataMeanDiffBias['Domain'] = 'MeanDiffBiasCorrected'

                    data2 = pd.concat([data, dataMeanDiffBias, AdjustedFinal])
                    print(data2)
                    kaput
                    
                    results.append([mycountry, myElement, myItem, round(MeanDiffBias[0], 1), MeanDiffBiasPros])
                    break
                    
        break
    df = pd.DataFrame(results)
    df.columns = ['Region', 'Element', 'Item', 'Correction', 'Correction-%']
    print(df)
    break


# if the user gives the element:
if myElement:
    correctionBias(myElement)
else:
    # Loop all elements:
    for myElement in elements:
        print(myElement)
        correctionBias(myElement)
