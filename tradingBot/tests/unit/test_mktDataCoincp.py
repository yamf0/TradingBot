##
# tests for mktDataCoincp
# @author Yael Martinez


from unittest import TestCase
from unittest.mock import patch, Mock

import sys
sys.path.insert(0, r'')

from tradingBot.mktDataModule.mktData import mktDataCoincp

class TestmktDataBaseCoincp(TestCase):

    ## Tests for coincap API
    # @class TestmktDataBaseCoincp

    
    def setUp(self):

        ## @fn setup
        # Creates the objet of mktDataCoincp for use in tests
    
        self.mktApi = mktDataCoincp()

    @patch("tradingBot.mktDataModule.mktDataCoincp.requests.get")
    def test_makeRequest_failed(self, mock_get):

        ## @fn test_makeRequest_failed 
        # tests a failed request, mocks requests.get call and returns a False in response.ok

        func = "assets"     
        params = {"payload" : "bictoin", "limit" : 1}
    
        mock_get.return_value.ok = False

        ret  = self.mktApi._makeRequest(baseUrl=func, params= params)

        self.assertTrue(mock_get.called)
        self.assertFalse(ret, "Request was false")

    @patch("tradingBot.mktDataModule.mktDataCoincp.requests.get")
    def test_makeRequest_pass(self, mock_get):

        ## @fn test_makeRequest_pass 
        # tests a pass request, mocks requests.get call and returns an expected json
        # Expected return from tested method is a json

        func = "assets"     
        params = {"payload" : "bictoin", "limit" : 1}
    
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            "data": {
                "id": "bitcoin",
                "rank": "1",
                "symbol": "BTC",
                "name": "Bitcoin",
                "supply": "18535643.0000000000000000",
                "maxSupply": "21000000.0000000000000000",
                "marketCapUsd": "344827255261.5952037507150844",
                "volumeUsd24Hr": "9072284012.4856937238886158",
                "priceUsd": "18603.4687472992009908",
                "changePercent24Hr": "-0.0136301131370071",
                "vwap24Hr": "18340.1515241528287361"
            },
            "timestamp": 1606075879247
        }

        ret  = self.mktApi._makeRequest(baseUrl=func, params= params)

       
        self.assertTrue(mock_get.called)
        self.assertIsInstance(ret, dict)
        

    def test_checkCond_coin_not_found(self):
        
        ## @fn test_checkCond_coin_not_found
        # test _checkCond method with a non existing coin

        ret = self.mktApi._checkCond(coin ="ADA", pair="BTC")

        self.assertFalse(ret, "Coin not found in dict")
    
    def test_checkCond_coin_found(self):

        ## @fn test_checkCond_coin_not_found
        # test _checkCond method with an existing coin

        ret = self.mktApi._checkCond(coin ="BTC", pair="ETH")

        self.assertTrue(ret, "Coin not found in dict")
