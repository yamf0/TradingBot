import requests

#TODO import a file containing all available coins // all available fiats
symbolMap = {"crypto" : [
            {"symbol" : "BTC", "name" : "bitcoin"},
            {"symbol" : "ETH", "name" : "ethereum"}
            ],
        "fiat": [
            {"symbol": "USDT", "name" : "us dollars"}
        ]}

class mktDataBase():
    """
        Class that handles the communication with the external market API 

        Methods:
            __init__():

    """

    apisInfo = {
        "coincap" : { "url" : "https://api.coincap.io/v2", "functions" : [
            {"id" : "markets", "url" : "https://api.coincap.io/v2/markets"},
            {"id" : "OCHL", "url" : "https://api.coincap.io/v2/candles"},
            {"id" : "assets", "url" : "https://api.coincap.io/v2/assets"}
        ]},
        "messari" : { "url" : "", "functions" : []}
        }
    def __init__(self, apiChoice):
        
        self._apiName = apiChoice
        self._apiUrl = self.apisInfo[apiChoice]["url"]
        self._apiFunctions = self.apisInfo[apiChoice]["functions"]
            
    def _get(self, func= None, params= None):
        """
            Method that makes a requests.get call to request the API for information

            Variables
                func: str           API function to be called (mapped in self.apisInfo)
                params: dict        parameters to pass with the request

            return:
                response:           request.response object
        """
        baseUrl = [item for item in self._apiFunctions if item.get("id") == func][0]["url"]
        response = requests.get(baseUrl, params = params)

        if not response.ok:
            #TODO Make logger message critical failed request
            #TODO RAISE ERROR
            return False
        
        return  response.json()

    def checkConnection (self):
        """
            Method that sends a generic message to the API server to check for connection
        """
        func = "assets"
        params = {"payload" : "bictoin", "limit" : 1}

        #! SHOULD I PUT IT IN A TRY EXCEPT BLOCK???
        res = self._get(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        #TODO Make logger message server connected
        return True


    def getCurrentData (self, coin= None, pair=None, exchange="binance"):
        """
            Method that gets the current price of a coin compared to pair

            Variables
                coin:           which coin price to obtain (e.g. BTC // ETH)
                pair:           which pair coin to obtain the price for (e.g. USDT // EUR)
                exchange:       which exchange to check the price from (e.g. binance // kraken)
            
            Return
                json:   json with the information obtained

        """
        #build Payload
        func = "markets"
        params = {"exchangeId" : exchange, "baseSymbol" : coin, "quoteSymbol" : pair}

        if coin not in [crypto["symbol"] for crypto in symbolMap["crypto"]]:
            #TODO RAISE ERROR COIN REQUESTED NOT IN AVAILABLE COINS
            return False

        if pair not in [crypto["symbol"] for crypto in symbolMap["crypto"]] + \
                        [fiat["symbol"] for fiat in symbolMap["fiat"]]:
            #TODO RAISE ERROR PAIR REQUESTED NOT IN AVAILABLE COINS
            return False
            
        res = self._get(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        #TODO Make logger message server connected
        return True

    def _getInterval(self, timeframe=None):
        """
            Method that constructs in the correct way the interval needed for the API

            Variables:
                timeframe: tuple    which time frame the data is to be obtained (e.g. (1, "min")//(1, "day"))

            Return:
                interval: str       CoinCap--- constructed as a letter and the number (e.g., d1 = 1 day)
        """
        if not isinstance(timeframe, tuple):
            #TODO RAISE ERROR TIME FRAME IS NOT A TUPLE
              return False

        number, timeInterval = timeframe
        if timeInterval[0] not in "mhwd":
            #TODO RAISE ERROR TimeInterval not in defined intervals
            return False
        timeInterval = timeInterval[0]

        return str(number) + timeInterval



    def OCHLData(self, coin= None, pair=None, exchange="binance", timeframe=None, start=None, end=None):
        """
            Method that gets the OCHL data for a specific coin in a specified timeframe
            @Variables
                coin: str                   which coin price to obtain (e.g. BTC // ETH)
                pair: str                   which pair coin to obtain the price for (e.g. USDT // EUR)
                timeframe: tuple            which time frame the data is to be obtained (e.g. (1, "min")//(1, "hour") //(1, "day")//(1, "week")) #!PRONE TO CHANGE
                start(optional): tuple      timestamp from which data starts (e.g. (10, 08, 2020) --> 
                                            10th of AUG of 2020 (day, month, year)) 
                end(optional): tuple        timestamp until which data ends (e.g. (10, 08, 2020) --> 
                                            10th of AUG of 2020 (day, month, year))  
            @Return
                json:   json with the information obtained
        """

        timeframe = self._getInterval(timeframe)

        if not timeframe:
            #TODO RAISE ERROR TimeInterval not in defined intervals
            return False

        #!build Payload CAN BE IN ANOTHER FUNCTION
        func = "OCHL"
        params = {"exchangeId" : exchange, "baseSymbol" : coin, "quoteSymbol" : pair,
                  "interval" : timeframe, "start": start, "end" : end}


        if coin not in [crypto["symbol"] for crypto in symbolMap["crypto"]]:
            #TODO RAISE ERROR COIN REQUESTED NOT IN AVAILABLE COINS
            return False

        if pair not in [crypto["symbol"] for crypto in symbolMap["crypto"]] + \
                        [fiat["symbol"] for fiat in symbolMap["fiat"]]:
            #TODO RAISE ERROR PAIR REQUESTED NOT IN AVAILABLE COINS
            return False
        
        #! UNTIL HERE

        res = self._get(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        #TODO Make logger message server connected
        return True    
