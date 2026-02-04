print("started")
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bs4 import BeautifulSoup as soup # HTML parser
import requests # Page requests
import re # Regular expressions

print("requesting url...")
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'} # How we wish to appear to CL
url = 'https://charlottesville.craigslist.org/search/msa?purveyor=owner#search=2~gallery~0'
raw = requests.get(url,headers=header) # Get page
print(raw)
print("done")

print("parsing html")
bsObj = soup(raw.content,'html.parser') # Parse the html
listings = bsObj.find_all(class_="cl-static-search-result") # Find all listings of the kind we want
print("done")

instrument_types = ['organ', 'piano', 'flute', 'guitar', 'amplifier', 'bass', 'trumpet', 'trombone', 'tuba', 'saxophone', 'drum']

print("collecting data")
data = [] # We'll save our listings in this object
for k in range( len(listings) ):
    title = listings[k].find('div',class_='title').get_text().lower()
    price = listings[k].find('div',class_='price').get_text()
    link = listings[k].find(href=True)['href']
    # Get brand from the title string:
    words = title.split()
    hits = [word for word in words if word in instrument_types] # Find brands in the title
    if len(hits) == 0:
        instrument = 'unknown'
    else:
        instrument = hits[0]
    # Get years from title string:
    regex_search = re.search(r'20[0-9][0-9]|19[0-9][0-9]', title ) # Find year references
    if regex_search is None: # If no hits, record year as missing value
        year = np.nan
    else: # If hits, record year as first match
        year = regex_search.group(0)
    #
    data.append({'title':title,'price':price,'year':year,'link':link,'instrument':instrument})

df = pd.DataFrame.from_dict(data)
df['price'] = df['price'].str.replace('$','')
df['price'] = df['price'].str.replace(',','')
df['price'] = pd.to_numeric(df['price'],errors='coerce')
df['year'] = pd.to_numeric(df['year'],errors='coerce')
df['age'] = 2025-df['year']
print(df.shape)
df.to_csv('cl_instruments.csv')
df.head()

# Some basic analysis 

print(df['price'].describe())
df['price'].hist()
plt.show()
print(df['age'].describe())
df['age'].hist(bins=20)
plt.show()

# examine instruments
print(df['instrument'].value_counts())
print(df.loc[:,['price','instrument']].groupby('instrument').describe())

ax = sns.scatterplot(data=df, x='age', y='price',hue='instrument')
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
plt.show()


df['log_price'] = np.log(df['price'])
df['log_age'] = np.log(df['age'])

ax = sns.scatterplot(data=df, x='log_age', y='log_price',hue='instrument')
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

print(df.loc[:,['log_price','log_age']].cov())
print(df.loc[:,['log_price','log_age']].corr())