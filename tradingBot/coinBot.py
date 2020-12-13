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

from tradingBot.mktDataModule.mktData import mktDataCoincp
from tradingBot.mktDataModule.mktData import mktDataBaseMessari


class coinBotBase():
    
    ## coinBotBase
    # @brief contains the Base class for coinBot
    # @var rPath path relative for TradinBot main folder
    rPath = os.getcwd()

    def __init__(self, coin, pair, counter):

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
        self.mktDataCoincap = mktDataCoincp()
        self.dbPath = os.path.join(self.rPath, "tradingBot", \
            "Data", self.coin, self.pair)

        self.dbOCHL = {}
        self.curOCHLData = {}
        self.dbByTmstp = {}
        self.intervals = {"5m": 300, "15m": 900, "30m": 1800, "1H": 3600, "2H": 7200, "1D": 86400}

        #Load data from db
        self._load_dbOCHL()
        self._populateDicts()
        #Check if data is updated
        self._getLatestTmstp(self._getUpdatedOCHL)

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

    def _load_dbOCHL(self):
        filenames = [candlesFiles for _, _, candlesFiles in os.walk(self.dbPath)][0]
        for fileInterval in filenames:
            with open(os.path.join(self.dbPath, fileInterval), "r") as f:
                dat = json.load(f)
                intervalName = fileInterval.split(".")[0]
                self.dbOCHL[intervalName] = dat
                     
    def _populateDicts(self):
        for key, val in self.dbOCHL.items():
            self.curOCHLData[key] = {"open": 0, "close": 0, "high": 0, "low": 0, "openTmstp": 0, "missingC": 0}      
            self.dbByTmstp[key] = {}
            for candle in val["data"]:
                self.dbByTmstp[key][candle["timestamp"]] = {key: val for key, val in candle.items() if key != "timestamp"}

    def __missingCandles(self, interval, tmstp, latestTmstp):

        misCandles = (tmstp - latestTmstp) / 1000 / self.intervals[interval]
        print("missing candles {} at {} interval".format(misCandles, interval))
        return misCandles 

    def _getOCHL(self, interval, end):
        reqInterval = self._getIntvl(interval)
        keys = list(self.dbByTmstp[interval])[::-1]
        start = [start for start in keys if "volume" in self.dbByTmstp[interval][start].keys()][0]

        data = self.mktDataCoincap.OCHLData(coin=self.coin, pair=self.pair, interval=reqInterval, start=start + 10000, end=end + 10000)
        if not data:
            #TODO raise exception data not obtained
            return False
        else:
            for dat in data["data"]:
               self.dbByTmstp[interval][dat["timestamp"]] = dat
            
            return True

    def _updateTmstpKeys(self, tmstp, interval):

        latestTmstp = max(self.dbByTmstp[interval].keys())
        misCandles = int((tmstp - latestTmstp) / 1000) / self.intervals[interval]
        for _ in range(int(misCandles)):
            newKey = latestTmstp + self.intervals[interval] * 1000
            latestTmstp = newKey
            self.dbByTmstp[interval][newKey] = {}

    def _getCurPrice(self, tmstp):
        data = self.mktDataCoincap.getCurData(coin=self.coin, pair=self.pair)
        price = float(data["data"][0]["price"])
        for key in self.dbByTmstp.keys():
            self._updateTmstpKeys(tmstp, key)
            
        for key, val in self.curOCHLData.items():
            tmstpKey = max(self.dbByTmstp[key].keys())
            val["close"] = price
            if not bool(self.dbByTmstp[key][tmstpKey]):
                val["open"] = price
                val["high"] = price
                val["low"] = price

                self._getOCHL(key, tmstpKey)
                #self._getLatestTmstp(self._getUpdatedOCHL, key)
            else:
                if val["high"] < price:
                    val["high"] = price
                elif val["low"] > price:
                    val["low"] = price
            
            self.dbByTmstp[key][tmstpKey] = val.copy()
                
                #val["openTmstp"] = self.dbOCHL[key]["end"] + self.intervals[key] * 1000 
            """if self.__missingCandles(key, tmstp, self.dbOCHL[key]["end"]) >= 1:
                if self.__missingCandles(key, tmstp, val["openTmstp"]) >= 1:"""

    def __getCurTmstpRounded(self):

        tmstp = int(time.time() * 1000)
        return tmstp

    def _getLatestTmstp(self, dataFunc):

        for key, val in self.dbOCHL.items():
            tmstp = self.__getCurTmstpRounded()
            lastestTmstp = val["end"]          
            #sleep if interval is close to next interval completion
            if ((tmstp - lastestTmstp) % self.intervals[key]) >= (self.intervals[key] - 10):
                    time.sleep(((self.intervals[key]) - (tmstp - lastestTmstp)) % (self.intervals[key])) 
            if self.__missingCandles(key, tmstp, lastestTmstp) >= 2:
                
                #Get the data with the injected function
                exitCode = dataFunc(key, lastestTmstp + self.intervals[key] * 1000, tmstp)
               
                print("UPDATE {}".format(tmstp))
                self._saveOCHL(key)
                           
    def _getIntvl(self, interval):
        
        interval = re.findall(r'[A-Za-z]+|\d+', interval)
        interval = (int(interval[0]), interval[1].lower()) 
        return interval

    def _getUpdatedOCHL(self, interval, start, end):
        
        key = interval
        interval = self._getIntvl(interval)
        data = self.mktDataCoincap.OCHLData(coin=self.coin, pair=self.pair, interval=interval, start=start, end=end + 1000)
        
        if not data:
            #TODO raise exception data not obtained
            return False
        print(len(self.dbOCHL[key]["data"]))
        self.dbOCHL[key]["end"] = data["end"]
        self.dbOCHL[key]["data"] = self.dbOCHL[key]["data"] + data["data"]
        print(len(self.dbOCHL[key]["data"]))
        #self.curOCHLData[key]["openTmstp"] = data["end"] + self.intervals[key] * 1000
        return True

    def _saveOCHL(self, intvlDb):
        with open(os.path.join(self.dbPath, intvlDb + ".json"), "w") as f:
            json.dump(self.dbOCHL[intvlDb], f, indent=2)


class coinBot(coinBotBase):

    ## CoinBot
    # inherits from CoinBotBase
    # @see CoinBotBase
    
    def __init__(self, coin, pair, counter):
        super().__init__(coin, pair, counter)

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
        tmstp = time.time() * 1000
        return int(tmstp) 

    def __setTmstp(self, tmstp):
        self._tmstp = tmstp
        self._notify()
        return None
    

if __name__ == "__main__":
    print(os.getcwd())
    counter = counter(30)

    coinBot("BTC", "USDT", counter)
       

