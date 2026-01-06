
## FBS transformations

The food balance sheet (FBS) by FAO has inconsistencies created by the change in methodology in 2014.

Food Balance Sheets at FAO: https://www.fao.org/4/X9892E/X9892e01.htm#TopOfPage

Vonderschmidt et al. (2024) "Analysis combining the multiple FAO food balance sheet datasets needs careful treatment" The Lancet Planetary Health, Volume 8, Issue 2, e69 - e71. Code available at https://github.com/axvonder/FAOComment.git

FAO compiles Food Balance Sheet (FBS) statistics for 191 countries, which present a comprehensive picture of the agrifood situation of a country in a specified reference period, showing the pattern of a country's food supply and utilizations.

Key differences between new and old Food Balance Sheet (FBS) methodology: https://files-faostat.fao.org/production/FBS/Key%20differences%20between%20new%20and%20old%20FBS%20June2022%20.pdf

### Details

In the FAO FBS database there are Elements, Items and Areas. Check the databases in 
- The new (2010-): https://www.fao.org/faostat/en/#data/FBS
- The historical (-2013): https://www.fao.org/faostat/en/#data/FBSH

The Elements in the new db are:
{511: 'Total Population - Both sexes',
 664: 'Food supply (kcal/capita/day)',
 661: 'Food supply (kcal)',
 674: 'Protein supply quantity (g/capita/day)',
 671: 'Protein supply quantity (t)',
 684: 'Fat supply quantity (g/capita/day)',
 681: 'Fat supply quantity (t)',
 5511: 'Production',
 5611: 'Import quantity',
 5072: 'Stock Variation',
 5911: 'Export quantity',
 5301: 'Domestic supply quantity',
 5521: 'Feed',
 5123: 'Losses',
 5154: 'Other uses (non-food)',
 5527: 'Seed',
 5170: 'Residuals',
 5142: 'Food',
 5131: 'Processing',
 645: 'Food supply quantity (kg/capita/yr)',
 5171: 'Tourist consumption'}

There are items and aggregated items such as 'Grand Total + (Total)' etc. There are also pointers to the list of items that constitutes an aggregated item , e.g. 'Grand Total > (List)'. These lists are omitted from the adjusted dataset.

 


### Delimitations

There are cases that are left out of the resulting adjusted dataset:

- If an element is not found in the historical dataset (-2013), we omit the data.

- If there are less than four overlapping years in the subset of Element-Area-Item joined from the new dataset and the historical dataset, we omit the data. These cases are saved separately into the 'fishy' dataset.

- If the adjusted values go below 0, they are set to zero.

- Examples that work well, see: https://github.com/myliheik/FBSadjusted/blob/main/notebooks/01-plotResults.ipynb
- Examples that have data gaps, no overlapping years, or other fishy issues: https://github.com/myliheik/FBSadjusted/blob/main/notebooks/02-plotFishyResults.ipynb

### Results

The resulting files are uploaded to Allas:


## Production and supply diversity


Moving on to: 

Kummu, M. et al. Interplay of trade and food system resilience: gains on supply diversity over time at the cost of trade independency. Glob. Food Sec. 24, 100360 (2020).
https://doi.org/10.1016/j.gfs.2020.100360

We will need 3-year rolling average of the time series and then Shannon index. 

### 3-year rolling average
