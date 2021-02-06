##
# CoinBot module 
# @author Yael Martinez
# @class coinBot
# @class coinBotBase

import time
import threading
import os
import queue
import json
import re

import sys
sys.path.insert(0, r'')

from tradingBot.binance.binanceModule import binanceAPI
from tradingBot.mktAnalysis.mktDataAnalysis import mktDataAnalysis


class coinBotBase():
    
    ## coinBotBase
    # @brief contains the Base class for coinBot
    # @var rPath path relative for TradinBot main folder
    rPath = os.getcwd()
    intervals = {"5m": 300, "15m": 900,
                          "30m": 1800, "1h": 3600, "2h": 7200, "1d": 86400}

    def __init__(self, coin, pair, counter, binanceAPI, indicators=None):

        ## 
        # @fn __init__
        #@brief initialize object with instance veriables
        #@param coin coin to analyze
        #@param pari pair to analyze
        #@param counter objet of the counter class
        #@var dbPath path to the current db of instance

        self.coin = coin
        self.pair = pair
        self.counter = counter
        self.indicators = indicators

        #API objects
        self.binApi = binanceAPI

        self.dbPath = os.path.join(self.rPath, "tradingBot", \
            "dataBase", self.coin, self.pair, "intervals")

        self.tmfrmVar = []
        self.listOfTmstp = {}

        #Load data from db
        self._loadDbOCHL()
        #Check if data is updated
        self._getCurPrice(int(time.time() * 1000))
         
        #Create MKT ANALYSIS
        self.mktAnalysis = mktDataAnalysis(coin=coin, pair=pair, coinBot=self,
                                           indicators=self.indicators)

        self.queue = queue.Queue()
        self.counter.addObsv(self)

        self._queueLoop()

    def _queueLoop(self):

        while True:
            try:
                tmstp = self.queue.get()[0]
                self._handleTask(tmstp)
            except queue.Empty:
                continue
            time.sleep(0.1)

    def _handleTask(self, tmstp):

        print("we got msg {} at tmstp {}".format(self.coin, tmstp))
        self._getCurPrice(tmstp)
        #TODO SEND ACT INDICATORS
        
        
    def _loadDbOCHL(self):
        #TODO LOAD ONLY OCHL DATA JSONS AND NOTHING MORE
        filenames = [candlesFiles for _, _, candlesFiles in os.walk(self.dbPath)][0]
        for fileInterval in filenames:
            with open(os.path.join(self.dbPath, fileInterval), "r") as f:
                dat = json.load(f)
                intervalName = fileInterval.split(".")[0]
                setattr(self, intervalName, dat)
                self.tmfrmVar.append(intervalName)
                #self.dbOCHL[intervalName] = dat

        for tmfrm in self.tmfrmVar:
            self.listOfTmstp[tmfrm] = []
            dat = getattr(self, tmfrm)
            for candle in dat["data"]:
                self.listOfTmstp[tmfrm] += [candle["timestamp"]]
                    
    def _saveOCHL(self, intvlDb):
        currDb = getattr(self, intvlDb)
        with open(os.path.join(self.dbPath, intvlDb + ".json"), "w") as f:
            json.dump(currDb, f, indent=2)

    def _getIntvl(self, interval):
        
        interval = re.findall(r'[A-Za-z]+|\d+', interval)
        interval = (int(interval[0]), interval[1].lower()) 
        return interval

    def _getOCHL(self, interval, start=None, end=None):

        reqInterval = self._getIntvl(interval)
        currDB = getattr(self, interval)
        if not start:
            start = currDB["end"]

        data = self.binApi._getOCHLHist(self.coin, self.pair, reqInterval, start, end)

        if not data:
            #TODO raise exception data not obtained
            return False
        else:
            for dat in data["data"]:
               self.listOfTmstp[interval] += [dat["timestamp"]]

            currDB["end"] = data["end"]
            currDB["data"] = currDB["data"][:-1]
            currDB["data"] = currDB["data"] + data["data"]
            setattr(self, interval, currDB)
            self._saveOCHL(interval)
            return True

    def _missCandles(self, tmstp, interval):
        latestTmstp = max(self.listOfTmstp[interval])
        misCandles = int((tmstp - latestTmstp) / 1000) / self.intervals[interval]
        return latestTmstp, misCandles

    def _updateTmstpKeys(self, tmstp, interval):

        latestTmstp, misCandles = self._missCandles(tmstp, interval)
        for _ in range(int(misCandles)):
            newKey = latestTmstp + self.intervals[interval] * 1000
            latestTmstp = newKey
            self.listOfTmstp[interval] += latestTmstp

    def _getCurData(self):
        varName = (self.coin + self.pair + "OCHL").lower()
        if hasattr(self.binApi, varName):
            data = getattr(self.binApi, varName)
        else:
            print("DATA UNAVAILABLE")
            return None
        return data

    def _getCurPrice(self, tmstp):
        #data = self.mktDataCoincap.getCurData(coin=self.coin, pair=self.pair)
        data = self._getCurData()
        if not data:
            return
        self.curPrice = float(data["data"][0]["close"])
        volume = float(data["data"][0]["volume"])
        for key in self.listOfTmstp.keys():
               
            latestTmstp, missCandles = self._missCandles(tmstp, key)
            if missCandles > 2:
                print("GET MISSING OCHL")
                self._getOCHL(key, end=tmstp)

        for tmfrm in self.tmfrmVar:
            val = getattr(self, tmfrm)
            curCandle = val["data"][-1]
            if (tmstp >= val["end"]) and (tmstp < (val["end"] + self.intervals[tmfrm] * 1000)):
                
                if "prevVol" not in curCandle.keys():
                    curCandle["prevVol"] = 0
                    curCandle["prevtmstp"] = data["data"][0]["timestamp"]
                if data["data"][0]["timestamp"] != curCandle["prevtmstp"]:
                    curCandle["prevVol"] = 0
                    curCandle["prevtmstp"] = data["data"][0]["timestamp"]
                 
                if int(tmstp / 1000) * 1000 == val["end"]:
                    curCandle["open"] = str(self.curPrice)
                    curCandle["high"] = str(self.curPrice)
                    curCandle["low"] = str(self.curPrice)
                    curCandle["close"] = str(self.curPrice)  
                    curCandle["volume"] = data["data"][0]["volume"]
                    curCandle["prevVol"] = volume
                    curCandle["status"] = "open"
                else:

                    curCandle["volume"] = str(float(curCandle["volume"]) + (float(data["data"][0]["volume"]) - curCandle["prevVol"]))
                    curCandle["prevVol"] = volume
                    if float(curCandle["high"]) < self.curPrice:
                        curCandle["high"] = str(self.curPrice)
                    elif float(curCandle["low"]) > self.curPrice:
                        curCandle["low"] = str(self.curPrice)
            else:
                self._getOCHL(tmfrm, start=tmstp - self.intervals[tmfrm] * 1000, end=tmstp)
                continue 
            curCandle["close"] = str(self.curPrice)       
            
            print("update at {} initial Tmspt {} real tmstp {} dict {}".format(
                tmfrm, val["data"][-1]["timestamp"], tmstp, curCandle))


class coinBot(coinBotBase):

    ## CoinBot
    # inherits from CoinBotBase
    # @see CoinBotBase
    
    def __init__(self, coin, pair, counter, binanceAPI, indicators=None):
        super().__init__(coin, pair, counter, binanceAPI, indicators=indicators)

#TODO DO WE NEED SOMEWAY TO KILL THE THREAD??


class counter():
    ##  
    #@class counter 
    #@brief the object that gets the current UNIX timestamp
    #@var _tmstp
    #variable that contains the current tmstp, this is the observed val
    #@var _observers
    #List containing all the observers subscribed

    _tmstp = 0
    _observers = []

    def __init__(self, interval):
        
        self.intvl = interval
        self.lock = threading.RLock()
        thread = threading.Thread(target=self._start, daemon=True)
        thread.start()

    def addObsv(self, Object):
        with self.lock:
            self._observers.append(Object)

    def rmvObsv(self, Object):
        with self.lock:
            self._observers.remove(Object)

    def _notify(self):
        with self.lock:
            for obsv in self._observers:
                obsv.queue.put([self._tmstp])

    def _start(self):
        
        while True:
            tmstp = self.__synchronize()
            self.__setTmstp(tmstp)
            time.sleep(1)

    def __synchronize(self):
        tmstp = self.__getTmstp()
        while int(tmstp / 1000) % (self.intvl) != 0:
            tmstp = self.__getTmstp()
            time.sleep(0.1)
        return tmstp

    def __getTmstp(self):
        tmstp = int(time.time()) * 1000
        return tmstp 

    def __setTmstp(self, tmstp):
        self._tmstp = tmstp
        self._notify()
        return None
    

if __name__ == "__main__":

    bAPI = binanceAPI()
    socket = bAPI.con2Socket()
    streams = [{"coin": "BTC", "pair": "USDT", "type": "OCHL", "interval": (1, "m")}]
    bAPI.multiSocket(socket, streams)
    print(os.getcwd())
    counter = counter(10)
    indicators = [{"indicator": "EMA", "period": 14, "interval": (1,"d")}]
    coinBot("BTC", "USDT", counter, bAPI, indicators=indicators)
       

