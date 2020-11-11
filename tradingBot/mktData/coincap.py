from requests import Request, Session
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from time import sleep, ctime



# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case


##GET INFO OF ALL COINS
url = "https://api.coincap.io/v2"
url = "https://api.coincap.io/v2/assets"
url = "https://api.coincap.io/v2/assets"
#url = "https://api.coincap.io/v2/assets?ids=bitcoin"

##GET INFO OF DETERMINED COIN
#url = "https://api.coincap.io/v2/assets/bitcoin"

##GET HISTORY OF ONE COIN  
#url = "https://api.coincap.io/v2/assets/ethereum/history?interval=m1"

##GET DATA OF COIN OF EXCHANGES
#url = "https://api.coincap.io/v2/assets/bitcoin/markets"

##ASK FOR SPECIFIC COIN AND MARKET with several more options
#url = "https://api.coincap.io/v2/markets?exchangeId=kraken&baseSymbol=ETH"
#url = "https://api.coincap.io/v2/markets?exchangeId=kraken&baseSymbol=ETH&quoteSymbol=USDT"



##GET HISTORICAL CANDLES
#url = "https://api.coincap.io/v2/candles?exchange=binance&interval=d1&baseId=ethereum&quoteId=tether"
##GET HISTORICAL FOR LOW INTERVALS SINCE " YEARS BACK"
#url = "https://api.coincap.io/v2/candles?exchange=binance&interval=m1&baseId=ethereum&quoteId=bitcoin&start=1540598400000&end=1540771200000"


#GET RATES SYMBOLS
#url = "https://api.coincap.io/v2/rates"


payload = {"search": "bitcoin", "limit" : 1}
headers= {}

for i in range(1):
    
    response = requests.get(url, headers=headers, params = payload)
    print(response)
    print(response.json())
    #print(response.text)
    response = json.loads(response.text)

    with open("example.json", "w") as f:
        json.dump(response,f,indent=2, separators=(",",":"))

    ts = int(response["timestamp"])
    print(ts)
    


    sleep(1)