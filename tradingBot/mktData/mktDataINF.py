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
    def getCurData (self, **kwargs):
        """
            Method that gets the current price of a coin compared to pair

            Variables
            
            Return
                json:   json with the information obtained

        """
        pass

    @abc.abstractmethod
    def OCHLData(self, **kwargs):
        """
            Method that gets the OCHL data for a specific coin in a specified timeframe
            @Variables

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
        pass

