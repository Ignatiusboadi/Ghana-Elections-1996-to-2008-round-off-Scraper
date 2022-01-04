from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import requests

homepage='https://ghanaelections.peacefmonline.com/pages/'

regions = ['ashanti', 'brongahafo', 'central', 'eastern', 'greateraccra', 'northern', 'uppereast',
           'upperwest', 'volta', 'western']

header = {
    "User-Agent":"Mozilla/5.0 (X11; Linux x84_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

years = ['1996', '2000', '2000a', '2004', '2008', '2008a']

data = {year:{region:{} for region in regions} for year in years}     #to be coerced into a pandas dataframe and exported to MS Excel
sub_data = {year:{region:{} for region in regions} for year in years} #to be stored in a json file

for year in years:
    j = 0
    for region in regions:
        print(year, region)
        for i in range(0, 276):
            try:
                link = requests.get(f'{homepage}{year}/{region}/{i}', headers=header)
                link_soup = bs(link.content, 'lxml')
                const = link_soup.title.text.split('-')[-2].strip()
                const_data = pd.read_html(link.text)[0]
                sub_data[year][region][const] = const_data.to_dict()
                data[year][region][const] = const_data
                regional_numbers[region].append(i)
                j += 1
                print(j, i, const)
                
ghana_elections = pd.read_html('https://africanelections.tripod.com/gh_detail.html#2000_Presidential_Election_(Second_Round)', header=0)
elections_1992 = ghana_elections[8]

elections_1992.rename(columns=elections_1992.iloc[0], inplace=True)
elections_1992.drop(labels=0, inplace=True)

#separate strings in candidate column which also contains party names into different columns
def party(x):
    if x[-4].isupper():
        return x[-4:]
    else:
        return x[-3:]
    
def candidate(x):
    if x[-4].isupper():
        return x[:-4]
    else:
        return x[:-3]
            except:
                pass
 
#Put Scraped data into json file                
with open('Ghana_Elections_Data_1996_2008.json', 'w') as file:
    json.dump(sub_data, file)
    
#Creating a dataframe for scraped data
elections_data = pd.DataFrame(columns=['Candidate', 'Votes', 'Share%', 'Constituency', 'Year', 'Region'])
for year in years:
    cur_data = data[year].copy()
    for region in cur_data:
        for constituency in cur_data[region]:
            const_data = cur_data[region][constituency]
            rows = const_data.shape[0]
            const_col = [' '.join(constituency.split()[:-1]) for i in range(rows)]
            region_col = [region.upper() for i in range(rows)]
            year_col = [year for i in range(rows)]
            const_data['Constituency'] = const_col
            const_data['Year'] = year_col
            const_data['Region'] = region_col
            
_2000 = elections_data[elections_data['Year'] == '2000']
other_years = elections_data[elections_data['Year'] != '2000']
other_years['Party'] = other_years['Candidate'].apply(lambda x: x[-3:])
other_years['Candidate'] = other_years['Candidate'].apply(lambda x: x[:-3])

_2000['Party'] = _2000['Candidate'].apply(party)
_2000['Candidate'] = _2000['Candidate'].apply(candidate)

gh_writer = pd.ExcelWriter('Ghana Elections 1992-2008.xlsx')
# elections_1992.to_excel(gh_writer, '1992', index=False)

for year in years:   
    if year == '2000':
        _2000.to_excel(gh_writer, year, index=False)
    else:
        other_years[other_years['Year'] == year].to_excel(gh_writer, year, index=False)
gh_writer.save()            

            elections_data = pd.concat([elections_data, const_data])
