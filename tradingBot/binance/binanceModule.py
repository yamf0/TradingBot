## @package binance
# binanceModule implementation for Binance API
# @author Yael Martinez

from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from binance.exceptions import *

import os
import json
import time

import sys
sys.path.insert(0, r'')

from tradingBot.resources.globals import symbolMap
from tradingBot.exceptions import BadKwargs, SymbolNotSupported


class binanceBaseAPI():

    ##@class binanceBaseAPI
    # Connects to the binance API using python-binance package

    def __init__(self):
        
        self._rPath = os.getcwd()
        self._OCHLdict = {}

        keyPath = os.path.join(self._rPath, "tradingBot", "access_keys", "API_KEY.json")
        key, secret = self.__importKey(keyPath)
        self.client = self._mkClient(key, secret)

    def __importKey(self, path):
        with open(path, "r") as f:
            key, secret = json.load(f).values()
        return key, secret
        
    def _mkClient(self, key, secret):
        client = Client(key, secret)
        return client

    def __pingServer(self):
        try:
            res = self.client.ping()
            return res
        except BinanceAPIException as ex:
            print("Exception: {}".format(ex))
        except BinanceRequestException as ex:
            print("Exception: {}".format(ex))
        #TODO LOG ERROR
        return False
    
    def _checkCond(self, **kwargs):

        # @fn _checkCond
        # @brief Method that checks that coin Conditions are met
        #         Coin requested does exists, pair requested does exist.
        # @param coin coin requested
        # @param pair pair requested
        # @exception EXCEPTION coin//pair not in available coins
        # @return boolean

        coin, pair, *_ = [kwargs[key] for key in kwargs.keys()]

        if coin not in [crypto["symbol"] for crypto in symbolMap["crypto"]]:
            
            raise(SymbolNotSupported(coin))

        if pair not in [crypto["symbol"] for crypto in symbolMap["crypto"]] + \
                [fiat["symbol"] for fiat in symbolMap["fiat"]]:
            # TODO RAISE ERROR PAIR REQUESTED NOT IN AVAILABLE COINS
            raise(SymbolNotSupported(pair))
        return True

    def __coinPair2Symbol(self, coin, pair):
        return coin.lower() + pair.lower()

    def __getIntvl(self, timeframe=None):

        # @fn _getIntvl
        # @brief Method that constructs in the correct way the interval needed for the API
        # @param timeframe which time frame the data is to be obtained (e.g. (1, "min")//(1, "day"))
        # @return interval constructed as a letter and the number (e.g., 1d = 1 day)

        if not isinstance(timeframe, tuple):
            
            raise(BadKwargs("Time interval is not a Tuple"))

        number, timeInterval = timeframe
        if timeInterval[0] not in "mhwd":
            
            raise(BadKwargs("Time frame not in supported time frames"))
        timeInterval = timeInterval[0]
        interval = str(number) + timeInterval

        return interval

    def _parseResponse(self, dataType, data):

        if dataType == "_getOCHLHist":
            res = {
                    "calledAPI": "BINANCE",
                    "start": "",
                    "end": "",
                    "interval": "",
                    "data": []
                }

            for candle in data:
                info = {
                    "open": candle[1],
                    "close": candle[2],
                    "high": candle[3],
                    "low": candle[4],
                    "volume": candle[5],
                    "timestamp": candle[0]
                    }
                res["data"].append(info)
            res["start"] = data[0][0]
            res["end"] = data[-1][0]

        elif dataType == "__processSocketMsg":
            
            return data

        elif "kline_" in dataType.split("@")[-1]:
            candleInfo = data["k"]
            res = {
                    "calledAPI": "BINANCE",
                    "start": "",
                    "end": "",
                    "interval": "",
                    "data": []
                }
            info = {
                "open": candleInfo["o"],
                "close": candleInfo["c"],
                "high": candleInfo["h"],
                "low": candleInfo["l"],
                "volume": candleInfo["v"],
                "timestamp": candleInfo["t"]
                }
            res["data"].append(info)
            res["start"] = candleInfo["t"]
            res["end"] = candleInfo["t"]
            res["interval"] = candleInfo["i"]
 
        return res
            
    def _getOCHLHist(self, coin, pair, interval, start, end=None):
        
        try:
            self._checkCond(coin=coin, pair=pair)
        except SymbolNotSupported as ex:
            print("Exception: {}".format(ex))
            return False
        try:
            interval = self.__getIntvl(interval)
        except BadKwargs as ex:
            print("Exception: {}".format(ex))
            return False
        symbol = self.__coinPair2Symbol(coin, pair).upper()

        data = self.client.get_historical_klines(symbol, interval, start, end)
        data = self._parseOCHL(self._getOCHLHist.___name__, data)
        data["interval"] = interval
        return data

    def con2Socket(self):
        binSocket = BinanceSocketManager(self.client)
        return binSocket
        
    def killSocket(self):
        pass

    def __processSocketMsg(self, msg):

        if msg['e'] == 'error':
            print("ERROR IN SOCKET")
        else:
            
            data = self._parseResponse(self.__processSocketMsg.__name__, msg)
            print("message type: {}".format(msg['e']))
            print(msg)
            # do something

    def __processMultiSocketMsg(self, msg):
          
        print("stream {}".format(msg["stream"]))
        data = self._parseResponse(msg["stream"], msg["data"])
        setattr(self, self._OCHLdict[msg["stream"]], data)
        # do something

    def candleSocket(self, binSocket, symbol, interval=None):
        conn_key = binSocket.start_kline_socket(symbol, self.__processSocketMsg, interval=KLINE_INTERVAL_1MINUTE)
        binSocket.start()
    
    def __formatStreams(self, streams):

        res = []
        streamType = {
            "agg": 'aggTrade',
            "trade": "trade",
            "OCHL": "kline_",
            "miniTicker": "miniTicker",
            "ticker": "ticker",
            "bookTicker": "bookTicker"
        }

        for stream in streams:
            sType = streamType[stream["type"]]
            try:
                self._checkCond(coin=stream["coin"], pair=stream["pair"])
            except SymbolNotSupported:
                print("Symbol is not supported, stream {} invalid".format(stream))
                continue
            symbol = self.__coinPair2Symbol(stream["coin"], stream["pair"])
            if stream["type"] == "OCHL":
                try:
                    interval = self.__getIntvl(stream["interval"])
                except BadKwargs:
                    print("Interval error, stream {} invalid".format(stream))
                    continue
                
                res.append(symbol + "@" + sType + interval)
            else:
                res.append(symbol + "@" + sType)

            varName = (stream["coin"] + stream["pair"] + stream["type"]).lower()
            setattr(self, varName, {})
            self._OCHLdict[res[-1]] = varName

        return res

    def multiSocket(self, binSocket, streams):

        streams = self.__formatStreams(streams)
        conn_key = binSocket.start_multiplex_socket(streams, self.__processMultiSocketMsg)
        binSocket.start()


class binanceAPI(binanceBaseAPI):

    def __init__(self):

        super().__init__()


if __name__ == "__main__":
    bAPI = binanceAPI()
    socket = bAPI.con2Socket()
    streams = [{"coin": "BTC", "pair": "USDT", "type": "OCHL", "interval": (1, "m")},
    {"coin": "ETH", "pair": "USDT", "type": "OCHL", "interval": (1, "m")}]

    bAPI.multiSocket(socket, streams)
    #dat = bAPI._getOCHLHist(coin="BTC", pair="USDT", interval=(1, "h"), start=1608390000000)
    #print(dat)

