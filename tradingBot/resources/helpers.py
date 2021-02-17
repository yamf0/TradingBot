##
# CoinBot module 
# @author Yael Martinez
# @class botManager

import threading
import time


class counter():
    
    ##  
    #@class counter 
    #@brief the object that gets the current UNIX timestamp
    #@var __tmstp
    #variable that contains the current tmstp, this is the observed val
    #@var _observers
    #List containing all the observers subscribed

    __tmstp = 0
    _observers = []

    def __init__(self, interval):
        
        ## 
        #@fn __init__
        #@brief constructs class and starts counter
        #@param interval int indicating trigger time in seconds

        self.intvl = interval
        self.lock = threading.RLock()
        thread = threading.Thread(target=self._start, daemon=True)
        thread.start()

    def addObsv(self, Object):
        
        ## 
        #@fn addObsv
        #@brief add to _observers list an Object instance
        #@param Object object instance to be notified

        with self.lock:
            self._observers.append(Object)

    def rmvObsv(self, Object):

        ## 
        #@fn rmvObsv
        #@brief remove from _observers list an Object instance
        #@param Object object instance to be removed

        with self.lock:
            self._observers.remove(Object)

    def _notify(self):

        ## 
        #@fn _notify
        #@brief ping to all object in _observers list
        
        with self.lock:
            for obsv in self._observers:
                obsv.queue.put([self.__tmstp])

    def _start(self):

        ## 
        #@fn _start
        #@brief create infinite counter loop
        
        while True:
            tmstp = self.__synchronize()
            self.__setTmstp(tmstp)
            time.sleep(1)

    def __synchronize(self):

        ## 
        #@fn __synchronize
        #@brief synchronize count to computer clock
        #each self.intvl must be sincrhonized with the computer clock
        #example: if invl is 10, only at 19:10:10, 19:10:20 will the trigger
        #occur
        #@return tmstp timestamp of trigger

        tmstp = self.__getTmstp()
        while int(tmstp / 1000) % (self.intvl) != 0:
            tmstp = self.__getTmstp()
            time.sleep(0.1)
        return tmstp

    def __getTmstp(self):

        ## 
        #@fn __getTmstp
        #@brief get the actual timestamp

        tmstp = int(time.time()) * 1000
        return tmstp 

    def __setTmstp(self, tmstp):

        ## 
        #@fn __setTmstp
        #@brief set the tmstp attribute and _notify method

        self.__tmstp = tmstp
        self._notify()
        return None