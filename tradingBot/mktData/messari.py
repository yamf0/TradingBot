from requests import Request, Session
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from time import sleep, ctime


#current data

url = "https://data.messari.io/api/v1/assets/eth/metrics/market-data"

response = requests.get(url)
response = json.loads(response.text)

#historic candles

url = "https://data.messari.io/api/v1/markets/binance-btc-usdt/metrics/price/time-series?start=2020-01-01&end=2020-02-01&interval=1d"

response1 = requests.get(url)
response1 = json.loads(response1.text)