


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

 


### delimitations

There are cases that are left out of the resulting adjusted dataset:

- If an element is not found in the historical dataset (-2013), we omit the data.

- If there are less than four overlapping years in the subset of Element-Area-Item joined from the new dataset and the historical dataset, we omit the data. These cases are saved separately into the 'fishy' dataset.

- If the adjusted values go below 0, they are set to zero.


