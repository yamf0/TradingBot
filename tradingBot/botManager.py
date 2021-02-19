##
# CoinBot module 
# @author Yael Martinez
# @class botManager

import os
import json
import threading
import queue
import time

import sys
sys.path.insert(0, r'')

from tradingBot.binance.binanceModule import binanceAPI
from tradingBot.coinBot import coinBot
from tradingBot.resources.helpers import counter, counterObserverINF


class botManager(counterObserverINF):

    ## botManager
    # @brief is the initializer of all intances required to function

    def __init__(self):
        
        #initialize counter
        self.counter = counter(10)

        #Load Run Scope        
        self.scope = self._loadRunScope()

        #create Binance conn
        self._binanceConn()
        self._actStreams()
        
        #TODO HERE INITIALIZE THE COUNTER AND CREATE THE BINANCE OBJECT

        #Create Queue and loop
        self._createQueue()
        self._counterSubscribe()

        self._queueLoop()

    def _createQueue(self):

        ##
        #@fn _createQueue
        #@brief creates the Queue for the class

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
        
        #When counter triggers check Scope
        if task[0] == "TimeTrigger":
            newScope = self._actScope()
            if newScope:
                self._actStreams()
            else: 
                return

    def _loadRunScope(self):

        with open(os.path.join(os.getcwd(), "tradingBot", "resources", "RunScope.json"), "r") as f:
            scope = json.load(f)
        return scope

    def _binanceConn(self):

        self.binanceObj = binanceAPI()
        self.binanceObjSocket = self.binanceObj.con2Socket()
    
    def _actStreams(self):

        self.binanceObj.actualizeMultiSocket(self.binanceObjSocket, self.scope)

    def _actCoinBots(self):
        pass

    def _actScope(self):

        newScope = self._loadRunScope()
        if newScope == self.scope:
            return False
        else:
            sortedScope = sorted(self.scope, key=lambda k: (k["coin"], k["pair"]))
            sortedNewScope = sorted(newScope, key=lambda k: (k["coin"], k["pair"]))
            self.scope = newScope
            #changes???
            return True

    def addCB(self):
        pass
        #TODO HERE ADD A NEW CB
    
    def delCB(self):
        pass
        #TODO HERE DELETE A COINBOT (PROCESS)


#TODO CLEAN THIS PART (ELIMINATE)
if __name__ == "__main__":

    botManager = botManager()

    bAPI = binanceAPI()
    socket = bAPI.con2Socket()
    streams = [{"coin": "BTC", "pair": "USDT", "type": "OCHL", "interval": (1, "m")}]
    bAPI.multiSocket(socket, streams)
    print(os.getcwd())

    indicators = [{"indicator": "EMA", "period": 14, "interval": (1, "d")},
                  {"indicator": "EMA", "period": 14, "interval": (1, "h")},
                  {"indicator": "SMA", "period": 14, "interval": (1, "h")},
                  {"indicator": "WMA", "period": 14, "interval": (1, "h")},
                  {"indicator": "RSI", "period": 14, "interval": (1, "h")}]
    coinBot("BTC", "USDT", counter, bAPI, indicators=indicators)
       
