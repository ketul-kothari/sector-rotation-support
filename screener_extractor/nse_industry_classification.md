The file nse-indices_industry-classification-structure-2023-07.pdf contains details on MES code, sector code, industry and basic industry codes.

C:\Users\ketul\repos\SectorRotation\support\screener_extractor\nse-indices_industry-classification-structure-2023-07.pdf

The screener.in has following url format 

https://www.screener.in/market/{MES_code}/{Sector_code}/{Industry_code}/{basic_industry_code/

Here is a sample url https://www.screener.in/market/IN07/IN0701/IN070101/IN070101001/

What  I want you to do is:

1. Read pdf and create csv file with following columns
MES_code, MES_name, Sector_code, Sector_name, Industry_code, Indsustry_name basic_industry_Code, basic_industry_name

This way we will have end to end mapping of basic industry.

2. Create a script that will iterateilvely form the url for each basic industry -> run the query and fetch the results of all the stocks from the page => I am interested in Name and Symbok, Market cap.

The Name column is actually a url which should be of format 
https://www.screener.in/company/HEROMOTOCO/consolidated/

In the above HEROMOTOCO is the name. Notice this list also contains BSE stocks -- where instead of name we will have number and they can be ignored.

The script should log in console which basic industry is navighating (1/182, industry name - xyzz).

If it is ignoring any stock it should document so.

Also the table on page can have pagination enabled, so the scirpt should navgate to multiple pages jf there. For that you have to analyze page structure.


In the end it should save the results in csv for all stocks with following format.

macro_sector_name,sector_name,industry_name,basic_industry_name,company,symbol,market_cap

The scrupts should be create ehre 


C:\Users\ketul\repos\SectorRotation\support\screener_extractor