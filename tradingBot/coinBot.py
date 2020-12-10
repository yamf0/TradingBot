##
# CoinBot module 
# @author Yael Martinez
# @class coinBot
# @class coinBotBase

import time
import threading
import os
import queue

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
        self.dbPath = os.path.join(self.rPath, "tradingBot", \
            "Data", self.coin, self.pair)

        self.queue = queue.Queue()
        self.counter.addObsv(self)

        self._queueLoop()

    def _queueLoop(self):
        while True:
            try:
                self.tmstp = self.queue.get()
                self._handleTask()
            except queue.Empty:
                continue
            time.sleep(0.1)

    def _handleTask(self):
        print("we got msg {}".format(self.coin))

    def __getCurTmstpRounded(self):
        tmstp = int(time.time())
        return tmstp

    def _getLatestTmstp(self):
        pass

    def _getUpdatedOCHL(self, tmstp, interval):
        pass

    def _saveOCHL(self, data, path):
        pass

    def _getCurPrice(self):
        pass
    
    
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
    counter = counter(10)

    coinBot("BTC", "USDT", counter)
       

