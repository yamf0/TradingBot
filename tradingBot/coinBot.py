##
# CoinBot module 
# @author Yael Martinez
# @class coinBot
# @class coinBotBase

import time
import threading

import sys
sys.path.insert(0, r'')

from tradingBot.mktDataModule.mktData import mktDataCoincp
from tradingBot.mktDataModule.mktData import mktDataBaseMessari


class coinBotBase():

    ## coinBotBase
    # @brief contains the Base class for coinBot
    def __init__(self):
        self.counter = counter(10)
        self.counter.addObsv(self)
    
    def _curTmstp(self):
        pass

    def _getLatestTmstp(self):
        pass

    def _matchTmstp(self, tmstp_1, tmstp_2):
        pass

    def _getUpdatedOCHL(self, tmstp, interval):
        pass

    def _saveOCHL(self, data, path):
        pass

    def _getCurPrice(self):
        pass
    
    def update(self):
        print("HELLO")
    pass


class coinBot(coinBotBase):

    ## CoinBot
    # inherits from CoinBotBase
    # @see CoinBotBase
    
    def __init__(self):
        super().__init__()


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
        thread = threading.Thread(target=self._start, daemon=False)
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
                obsv.update()

    def _start(self):
        
        while True:
            tmstp = self.__synchronize()
            self.__setTmstp(tmstp)

    def __synchronize(self):
        tmstp = self.__getTmstp()
        while tmstp % self.intvl != 0:
            tmstp = self.__getTmstp()
            if str(tmstp).split(".")[-1] > "9":
                tmstp = int(tmstp)
            time.sleep(0.1)
        return tmstp

    def __getTmstp(self):
        tmstp = time.time()
        return tmstp

    def __setTmstp(self, tmstp):
        self._tmstp = tmstp
        self._notify()
        return None
    

if __name__ == "__main__":

    o = coinBot()
