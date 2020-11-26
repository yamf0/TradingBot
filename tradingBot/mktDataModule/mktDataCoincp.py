## @package mktDataCoincap
# mktData implementation for Coincap API, based in mktData interface
# @author Yael Martinez

import sys
sys.path.insert(0, r'')

from tradingBot.mktDataModule.mktDataINF import mktDataINF

import requests
import datetime
import os

from tradingBot.resources.globals import symbolMap



class mktDataBaseCoincp(mktDataINF):
    ## Coincap class
    # @class mktDataBaseCoincp 
    # @see mktDataINF
    
    ## @var apiInfo
    # contains the Url to access different api calls
    apiInfo = {
        "coincap" : { "url" : "https://api.coincap.io/v2", "functions" : [
            {"id" : "markets", "url" : "https://api.coincap.io/v2/markets"},
            {"id" : "OCHL", "url" : "https://api.coincap.io/v2/candles"},
            {"id" : "assets", "url" : "https://api.coincap.io/v2/assets"}
        ]}}
        
    def __init__(self):
        self._apiFunctions = self.apiInfo["coincap"]["functions"]
        self.path = os.path.dirname(os.path.abspath(__file__))


    def _makeRequest(self, baseUrl= None, params= None):

        ## @fn _makeRequest 
        # @brief Method that uses requests.get() call to request the API for information
        # @param baseUrl API function to be called
        # @param params Parameters to pass with the request
        # @exception EXCEPTION response not OK
        # @return response  resonse object json

        baseUrl = [item for item in self._apiFunctions if item.get(
            "id") == baseUrl][0]["url"]
        response = requests.get(baseUrl, params=params)


        if not response.ok:
            #TODO Make logger message critical failed request
            #TODO RAISE ERROR
            print(response.json()["error"])
            return False
        
        return  response.json()
    
    def _getIntvl(self, timeframe=None):
    
        ## @fn _getIntvl 
        # @brief Method that constructs in the correct way the interval needed for the API
        # @param timeframe which time frame the data is to be obtained (e.g. (1, "min")//(1, "day"))
        # @return interval constructed as a letter and the number (e.g., d1 = 1 day)
     
        if not isinstance(timeframe, tuple):
            #TODO RAISE ERROR TIME FRAME IS NOT A TUPLE
              return False

        number, timeInterval = timeframe
        if timeInterval[0] not in "mhwd":
            #TODO RAISE ERROR TimeInterval not in defined intervals
            return False
        timeInterval = timeInterval[0]

        return timeInterval + str(number)

    def _checkCond(self, **kwargs):
        
        
        ## @fn _checkCond
        # @brief Method that checks that coin Conditions are met 
        #         Coin requested does exists, pair requested does exist.
        # @param coin coin requested
        # @param pair pair requested
        # @exception EXCEPTION coin//pair not in available coins
        # @return boolean   
        
        coin, pair = [val for val in kwargs.values()]

        if coin not in [crypto["symbol"] for crypto in symbolMap["crypto"]]:
            #TODO RAISE ERROR COIN REQUESTED NOT IN AVAILABLE COINS
            return False

        if pair not in [crypto["symbol"] for crypto in symbolMap["crypto"]] + \
                        [fiat["symbol"] for fiat in symbolMap["fiat"]]:
            #TODO RAISE ERROR PAIR REQUESTED NOT IN AVAILABLE COINS
            return False
        
        return True

    """ def _convertTimestamp(self, timestamp=None):
        
        ## @fn _convertTimestamp
        # @brief Methot that converts UNIX timestamp to DD-MM-YYYY_HH-MM-SS.00000 format
        # @param timestamp timestampt to convert
        # @return time converted timestamp
        
        timestamp = datetime.datetime.fromtimestamp(timestamp/1000)\
                                    .strftime('%d-%m-%Y--%H-%M-%S.%f')
                            
        return timestamp"""


    def _parseResponse(self, func=None, info=None):
        
        ## @fn _parseResponse 
        # @brief Method that parse the response in a defined json structure
        # @param func the type of json to be parsed
        # @param info json to be parsed
        # @return res the json produced 
        api = "coincap"
        if func == "getCurData":
            data = info["data"][0]
            exchange = data["exchangeId"]
            coin = data["baseSymbol"]
            pair = data["quoteSymbol"]
            price = data["priceQuote"]
            volume24Hr = data["volumeUsd24Hr"]
            percentChangeLast24 = data["percentExchangeVolume"]
            timestamp = data["updated"]
            
            
            res = {
                "calledAPI": api,
                "exchangeId" : exchange,
                "data": [
                {
                    "coin" : coin,
                    "pair" : pair,
                    "price" : price,
                    "volume24Hr" : volume24Hr,
                    "percentChangeLast24" : percentChangeLast24,
                    "timestamp" : timestamp
                }
            ]
            }

            return res
        elif func == "OCHLData":
            res = {
                "start" : "",
                "end" : "",
                "interval" : "",
                "data" : []
            }            
            data = info["data"]
            for d in data:

                timestamp = d["period"]
                dDict = {
                        "open" : d["open"],
                        "close" : d["close"],
                        "high" : d["high"],
                        "low" : d["low"],
                        "volume" : d["volume"],
                        "timestamp" : timestamp
                    }
                res["data"].append(dDict)
            res["start"] = res["data"][-1]["timestamp"]  
            res["end"] = res["data"][0]["timestamp"]  
            res["calledAPI"] = api
            return res

    def checkConnection (self):
        
        ## @fn checkConnection 
        # @brief Method that sends a generic message to the API server to check for connection
        # @return boolean
        
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
        
        ## @fn getCurData
        # @brief Method that gets the current price of a coin compared to pair
        #
        # Uses method _makeRequest and _cehckCond
        #
        # @param coin which coin price to obtain (e.g. BTC // ETH)
        # @param pair which pair coin to obtain the price for (e.g. USDT // EUR)
        # @param exchange which exchange to check the price from (e.g. binance // kraken)
        # @see _makeRequest, _checkCond
        # @return json with the information obtained

        
        #Make sure No error is given when not arguments are passed
        methodVar = {"coin" : "BTC", "pair" : "USDT", "exchange" : "binance"}

        methodVar.update(kwargs)

        coin, pair, exchange, *_= [methodVar[key] for key in methodVar.keys()]

        if not self._checkCond(coin=coin, pair=pair):
            return False

        #build Payload
        func = "markets"
        params = {"exchangeId" : exchange, "baseSymbol" : coin, "quoteSymbol" : pair}
            
        res = self._makeRequest(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        parsedInf = self._parseResponse(func= "getCurData", info= res)

        #TODO Make logger message server connected
        return parsedInf


    def OCHLData(self, **kwargs):
        
        ## @fn OCHLData
        # @brief Method that gets the OCHL data for a specific coin in a specified interval
        #
        # Uses method _makeRequest and _cehckCond
        #
        # @param coin which coin price to obtain (e.g. BTC // ETH)
        # @param pair which pair coin to obtain the price for (e.g. USDT // EUR)
        # @param interval which time frame the data is to be obtained (e.g. (1, "min")//(1, "hour") //(1, "day")//(1, "week"))
        # @param start (optional) timestamp from which data starts (e.g. (10, 08, 2020) --> 
        #                                 10th of AUG of 2020 (day, month, year)) 
        # @param end (optional) timestamp until which data ends (e.g. (10, 08, 2020) --> 
        #                                 10th of AUG of 2020 (day, month, year))  
        #
        # @exception EXCEPTION time interval is not permited
        # @return json with the information obtained
        
        #Make sure No error is given when not arguments are passed
        methodVar = {"coin" : "bitcoin", "pair" : "tether", "exchange" : "binance", "interval" : None , "start" : None, "end" : None}

        methodVar.update(kwargs)
        

        coin, pair, exchange, interval, start, end, *_= [methodVar[key] for key in methodVar.keys()]

        interval = self._getIntvl(interval)

        if not interval:
            #TODO RAISE ERROR TimeInterval not in defined intervals
            return False

        if not self._checkCond(coin=coin, pair=pair):
            return False

        coin = [name["id"] for coinType in symbolMap.values() for name in coinType if name["symbol"] == coin][0] 
        pair = [name["id"] for coinType in symbolMap.values() for name in coinType if name["symbol"] == pair][0]

        
            
        #!build Payload CAN BE IN ANOTHER FUNCTION
        func = "OCHL"
        params = {"exchange" : exchange, "baseId" : coin, "quoteId" : pair,
                  "interval" : interval, "start": start, "end" : end}

        res = self._makeRequest(func, params)

        if not res:
            #TODO Logger connection with server down
            return False

        parsedInf = self._parseResponse(func= "OCHLData", info= res)
        parsedInf["interval"] = interval

        #TODO Make logger message server connected
        return parsedInf    


if __name__ == "__main__":
    
    o = mktDataBaseCoincp()
    o.checkConnection()
    o.getCurData(coin="BTC",pair="USDT")
    o.OCHLData(coin="ETH", pair="USDT", interval=(1,"m"))
