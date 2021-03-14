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

#TODO CLEAN THE IMPORT OF BINANCE
from tradingBot.binance.binanceModule import binanceAPI
from tradingBot.mktAnalysis.mktDataAnalysis import mktDataAnalysis
from tradingBot.mktStrategy.mktStrategy import mktStrategy
from tradingBot.resources.helpers import counter, counterObserverINF


class coinBotBase(counterObserverINF):
    
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
        #@param pair pair to analyze
        #@param counter object of the counter class
        #@var dbPath path to the current db of instance

        self.coin = coin
        self.pair = pair
        self.strategiesIndic = []
        self.counter = counter
        self.indicators = indicators
        self.runScPath = os.path.join(self.rPath, "tradingBot", \
            "resources", "RunScope.json")
        self.strPath = os.path.join(self.rPath, "tradingBot", \
            "resources", "strategies.json")

        #Open resources
        with open(self.runScPath, 'r') as f:
            self.RunScope = json.load(f)
        with open(self.strPath, 'r') as f:
            self.strategies = json.load(f)
        self.RunScope = self.RunScope['Scope']
        self.strategies = self.strategies['Strategies']
        
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

        #Define the strategies that are needed
        for line in self.RunScope:
            if line["coin"] == self.coin and line["pair"] == self.pair:
                self.desiredStr = line["strategy"]

        for line in self.strategies:
            if line["strategy"] in self.desiredStr:
                for indic in line['indicators']:
                    self.strategiesIndic.append(indic)

        #Create MKT ANALYSIS
        self.mktAnalysis = mktDataAnalysis(coin=coin, pair=pair, coinBotObj=self, \
            indicators=self.strategiesIndic)   

        self._createQueue()
        self._counterSubscribe()
        self._queueLoop()
    
    def checkScope(self):
        with open(self.runScPath, 'r') as f:
            self.RunScope = json.load(f)
        with open(self.strPath, 'r') as f:
            self.strategies = json.load(f)
        self.RunScope = self.RunScope['Scope']
        self.strategies = self.strategies['Strategies']    
        for line in self.RunScope:
            if line["coin"] == self.coin and line["pair"] == self.pair:
                desiredStr_1 = line["strategy"]       
        if self.desiredStr != desiredStr_1:
            self.strategiesIndic = []
            self.desiredStr = desiredStr_1
            self.mktAnalysis.delAllIndicator()
            for line in self.strategies:
                if line["strategy"] in self.desiredStr:
                    for indic in line['indicators']:
                        self.strategiesIndic.append(indic)  
            for indic in self.strategiesIndic:
                self.mktAnalysis.newIndicator(indicator=indic["indicator"], period=indic["period"],\
                    interval=indic["interval"])
            return False
        return True

    def _createQueue(self):

        ##
        #@fn _createQueue
        #@brief creates the Queue for the class

        self.mktStrategy = mktStrategy(coin=None, pair=None, coinBotObj=self, 
                                   dataAnalysisObj=self.mktAnalysis)
        self.queue = queue.Queue()

    def _counterSubscribe(self):

        ##
        #@fn _counterSubscribe
        #@brief Subscribes to notification by Counter Obj

        self.counter.addObsv(self)

    def _counterUnsubscribe(self):

        ##
        #@fn _counterUnsubscribe
        #@brief unsubscribes to notification by Counter Obj
        
        self.counter.rmvObsv(self)

    def _queueLoop(self):

        ## 
        #@fn __queueLoop
        #@brief infinite loop that gets tasks on Queue

        while True:
            try:
                task = self.queue.get()
                self._handleTask(task)
            except queue.Empty:
                continue
            time.sleep(0.1)

    def _handleTask(self, task):
        
        ## 
        #@fn __handleTask
        #@brief will actualize DB and Indicators
        #@param tmstp current timestamp
        if task[0] == "TimeTrigger":
            tmstp = task[1]
            print("we got msg {} at tmstp {}".format(self.coin, tmstp))
            self._getCurPrice(tmstp)
            #TODO SEND ACT INDICATORS
            self.mktAnalysis.actlDB()
            if self.checkScope():
                self.mktAnalysis.actlIndicators()
            print("INDICATORS ACTUALIZED")
            self.mktStrategy.test()
    
    def _loadDbOCHL(self):
        
        ## 
        #@fn _loadDbOCHL
        #@brief loads all jsons' candles DB
     
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

        ## 
        #@fn _saveOCHL
        #@brief save the actualized DB in jsons
        #@param intvDb name of interval to save

        currDb = getattr(self, intvlDb)
        with open(os.path.join(self.dbPath, intvlDb + ".json"), "w") as f:
            json.dump(currDb, f, indent=2)

    def __getIntvl(self, interval):
        
        ## 
        #@fn __getIntvl
        #@brief format the interval
        #@param interval interval name
        #@return interval formated interval

        interval = re.findall(r'[A-Za-z]+|\d+', interval)
        interval = (int(interval[0]), interval[1].lower()) 
        return interval

    def _getOCHL(self, interval, start=None, end=None):

        ## 
        #@fn _getOCHL
        #@brief get OCHL data from Binance API
        #@param interval interval name
        #@param start starting timestamp
        #@param end last timestamp
        #@return boolean 
        
        reqInterval = self.__getIntvl(interval)
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
        
        ## 
        #@fn _missCandles
        #@brief get the number of missing candles since timestamp
        #@param tmstp timestamp to compare to
        #@param interval interval name
        #@return latestTmstp last available timestamp
        #@return misCandles int of missing candles

        latestTmstp = max(self.listOfTmstp[interval])
        misCandles = int((tmstp - latestTmstp) / 1000) / self.intervals[interval]
        return latestTmstp, misCandles

    def _getCurData(self):

        ## 
        #@fn _getCurData
        #@brief get the current price of coin with binanceAPI
        #@return data dictionary of 1m candle price

        varName = (self.coin + self.pair + "OCHL").lower()
        if hasattr(self.binApi, varName):
            data = getattr(self.binApi, varName)
        else:
            print("DATA UNAVAILABLE")
            return None
        return data

    def _getCurPrice(self, tmstp):
        
        ## 
        #@fn _getCurPrice
        #@brief form and update the DB with current prices
        #This method will update all missing candles through _getOCHL method
        #Then will update the current candle price and volume
        #Once a new candle is produced, the method updates the candle with _getOCHL method
        #@param tmstp actual timestamp 

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

   
#TODO CLEAN THIS PART (ELIMINATE)
if __name__ == "__main__":

    bAPI = binanceAPI()
    socket = bAPI.con2Socket()
    streams = [{"coin": "BTC", "pair": "USDT", "type": "OCHL", "interval": (1, "m")}]
    bAPI.multiSocket(socket, streams)
    print(os.getcwd())
    counter = counter(10)
    coinBot("BTC", "USDT", counter, bAPI)
