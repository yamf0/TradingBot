from requests import Request, Session
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from time import sleep, ctime



# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case


##GET INFO OF ALL COINS
url = "https://data.messari.io/api/v2/assets"

params = {"search" : "ethereum", "fields" : "id,slug,symbol,metrics/market_data/price_usd", "marketKey" : "binance", "limit" : 1}

response = requests.get(url,  params = params)
print(response.url)
response = json.loads(response.text)
