"""
@package mktDataCoincap
mktData implementation for Coincap API, based in mktData interface
@author Yael Martinez
"""

from tradingBot.mktData.mktDataINF import mktDataINF

import requests

#TODO import a file containing all available coins // all available fiats
symbolMap = {"crypto" : [
            {"symbol" : "BTC", "name" : "bitcoin"},
            {"symbol" : "ETH", "name" : "ethereum"}
            ],
        "fiat": [
            {"symbol": "USDT", "name" : "us dollars"}
        ]}




class mktDataBaseCoincp(mktDataINF):
    """
        @class that handles the communication with the external market API 
        @see mktDataINF
    """

    apiInfo = {
        "coincap" : { "url" : "https://api.coincap.io/v2", "functions" : [
            {"id" : "markets", "url" : "https://api.coincap.io/v2/markets"},
            {"id" : "OCHL", "url" : "https://api.coincap.io/v2/candles"},
            {"id" : "assets", "url" : "https://api.coincap.io/v2/assets"}
        ]}}
    def __init__(self):
        self._apiFunctions = self.apiInfo["coincap"]["functions"]

    def _makeRequest(self, func= None, params= None):
        """
            @fn _makeRequest 
            @breif A function that uses requests.get() call to request the API for information

            @param func API function to be called
            @param params Parameters to pass with the request
            @exception EXCEPTION response not OK
            @return response  resonse object json
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
        res = self._makeRequest(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        #TODO Make logger message server connected
        return True


    def getCurData (self, **kwargs):
        """
            Method that gets the current price of a coin compared to pair

            Variables
                coin:           which coin price to obtain (e.g. BTC // ETH)
                pair:           which pair coin to obtain the price for (e.g. USDT // EUR)
                exchange:       which exchange to check the price from (e.g. binance // kraken)
            
            Return
                json:   json with the information obtained

        """
        #Make sure No error is given when not arguments are passed
        methodVar = {"coin" : None, "pair" : None, "exchange" : "binance"}

        methodVar.update(kwargs)

        coin, pair, exchange, _= [methodVar[key] for key in methodVar.keys()]

        if not self._checkCond(coin=coin, pair=pair):
            return False

        #build Payload
        func = "markets"
        params = {"exchangeId" : exchange, "baseSymbol" : coin, "quoteSymbol" : pair}
            
        res = self._makeRequest(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        #TODO Make logger message server connected
        return True

    def _getIntvl(self, timeframe=None):
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

    def _checkCond(self, coin=None, pair=None):
        """
            Method that checks that coin Conditions are met
            Coin requested does exists, pair requested does exist...
        """
        if coin not in [crypto["symbol"] for crypto in symbolMap["crypto"]]:
            #TODO RAISE ERROR COIN REQUESTED NOT IN AVAILABLE COINS
            return False

        if pair not in [crypto["symbol"] for crypto in symbolMap["crypto"]] + \
                        [fiat["symbol"] for fiat in symbolMap["fiat"]]:
            #TODO RAISE ERROR PAIR REQUESTED NOT IN AVAILABLE COINS
            return False
        
        return True

    def OCHLData(self, **kwargs):
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
        #Make sure No error is given when not arguments are passed
        methodVar = {"coin" : None, "pair" : None, "exchange" : "binance", "timeframe" : None , "start" : None, "end" : None}

        methodVar.update(kwargs)

        coin, pair, exchange, timeframe, start, end, _= [methodVar[key] for key in methodVar.keys()]

        timeframe = self._getIntvl(timeframe)

        if not timeframe:
            #TODO RAISE ERROR TimeInterval not in defined intervals
            return False

        if not self._checkCond(coin=coin, pair=pair):
            return False
            
        #!build Payload CAN BE IN ANOTHER FUNCTION
        func = "OCHL"
        params = {"exchangeId" : exchange, "baseSymbol" : coin, "quoteSymbol" : pair,
                  "interval" : timeframe, "start": start, "end" : end}

        res = self._makeRequest(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        #TODO Make logger message server connected
        return True    


