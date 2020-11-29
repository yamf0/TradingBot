import abc


class mktDataINF(abc.ABC):

    # @class mktDataINF
    # Interface for all data APIs

    @abc.abstractmethod
    def _makeRequest(self, baseUrl=None, params=None):

        # @fn _makeRequest
        # Abstract method to make request with requests lib
        # @param baseUrl base URl to call
        # @param params dict contianing the requested parameters

        pass

    @abc.abstractmethod
    def checkConnection(self):

        # @fn checkConnection
        # Abstract method to check API connection

        pass

    @abc.abstractmethod
    def getCurData(self, **kwargs):

        # @fn getCurData
        # Abstract method to get current data of coin

        pass

    @abc.abstractmethod
    def OCHLData(self, **kwargs):

        # @fn OCHLData
        # Abstract method to get candles historic data

        pass

    @abc.abstractmethod
    def _checkCond(self, **kwargs):

        # @fn _checkCond
        # Abstract method to check correctness of passed arguments

        pass

    @abc.abstractmethod
    def _parseResponse(self, func=None, info=None):

        # @fn _parseResponse
        # gets a function name and parse the response in a defined json structure
        # @param func the type of json to be parsed
        # @param info dict passed

        pass
