import json

import pandas as pd
import requests
from bs4 import BeautifulSoup

ZILLOW_URL = "https://www.zillow.com/homes/for_rent/1-_beds/"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 "
                  "Safari/537.36",
    "accept-language": "en-US",
}

# need the 'wants' to grab all the pages of results
params = {
    "searchQueryState": '{"usersSearchTerm":"San Francisco, CA","mapBounds":{"north":37.884030776813404,'
                        '"east":-122.3066434038086,"south":37.666392961164114,"west":-122.5600155961914},'
                        '"isMapVisible":true,"filterState":{"isForSaleByAgent":{"value":false},"isForSaleByOwner":{'
                        '"value":false},"isNewConstruction":{"value":false},"isForSaleForeclosure":{"value":false},'
                        '"isComingSoon":{"value":false},"isAuction":{"value":false},"isForRent":{"value":true},'
                        '"isAllHomes":{"value":true},"monthlyPayment":{"max":3000},"price":{"max":597262},'
                        '"beds":{"min":1,"max":1}},"isListVisible":true,"mapZoom":12,"regionSelection":[{'
                        '"regionId":20330,"regionType":6}],"pagination":{}}',
    "wants": json.dumps(
        {
            "cat1": ["listResults", "mapResults"],
            "cat2": ["total"]
        }
    ),
    "requestId": 3
}

response = requests.get(ZILLOW_URL, headers=headers, params=params).content

soup = BeautifulSoup(response, 'html.parser')

# iterating through the pages in zillow for results
data = json.loads(soup.select_one("script[data-zrr-shared-data-key]").contents[0].strip("!<>-"))
all_data = data['cat1']['searchResults']['listResults']

url_list = []
prices_list = []
addresses_list = []
index = 0
for data in all_data:
    url_list.append(all_data[index]["detailUrl"])
    addresses_list.append(all_data[index]["address"])
    try:
        prices_list.append(all_data[index]["price"])
    except KeyError:
        prices_list.append(all_data[index]["units"][0]["price"])
    index += 1

# need to add the url_start to some urls
url_start = "https://www.zillow.com"
final_houses_url_list = [url_start + item if url_start not in item else item for item in url_list]

# convert to dataframe and export as csv
df = pd.DataFrame({
    "url": final_houses_url_list,
    "prices": prices_list,
    "addresses": addresses_list
})
df.to_csv("house_search_results.csv")
