import abc


class mktDataINF(abc.ABC):
    """
        Class that handles the communication with the external market API 

        Methods:
    """
    @abc.abstractmethod       
    def _makeRequest(self, func= None, params= None):
        """
            Method that makes a requests.get call to request the API for information

            Variables
                func: str           API function to be called (mapped in self.apisInfo)
                params: dict        parameters to pass with the request

            return:
                response:           request.response object
        """
        pass

    @abc.abstractmethod       
    def checkConnection (self):
        """
            Method that sends a generic message to the API server to check for connection
        """
        pass

    @abc.abstractmethod       
    def getCurrentData (self, coin= None, pair=None, exchange="binance"):
        """
            Method that gets the current price of a coin compared to pair

            Variables
                coin:           which coin price to obtain (e.g. BTC // ETH)
                pair:           which pair coin to obtain the price for (e.g. USDT // EUR)
                exchange:       which exchange to check the price from (e.g. binance // kraken)
            
            Return
                json:   json with the information obtained

        """
        pass

    @abc.abstractmethod
    def OCHLData(self, coin= None, pair=None, exchange="binance", timeframe=None, start=None, end=None):
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
        pass

    @abc.abstractmethod
    def _checkCond (self, **kwargs):
        """
            Method that gets the arguments passed in to a method called and checks that conditions are met
            Coin requested does exists, pair requested does exist...

        """


