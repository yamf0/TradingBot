##
# tests for mktDataCoincp
# @author Yael Martinez


from tradingBot.mktDataModule.mktData import mktDataCoincp
from tradingBot.exceptions import BadKwargs, SymbolNotSupported
from unittest import TestCase
from unittest.mock import patch

import sys
sys.path.insert(0, r'')


class TestmktDataBaseCoincp(TestCase):

    # Tests for coincap API
    # @class TestmktDataBaseCoincp

    def setUp(self):

        # @fn setup
        # Creates the objet of mktDataCoincp for use in tests

        self.mktApi = mktDataCoincp()

    @patch("tradingBot.mktDataModule.mktDataCoincp.requests.get")
    def test_makeRequest_failed(self, mock_get):

        # @fn test_makeRequest_failed
        # tests a failed request, mocks requests.get call and returns a False in response.ok

        func = "assets"
        params = {"payload": "bictoin", "limit": 1}

        mock_get.return_value.ok = False

        ret = self.mktApi._makeRequest(baseUrl=func, params=params)

        self.assertTrue(mock_get.called)
        self.assertFalse(ret, "Request was false")

    @patch("tradingBot.mktDataModule.mktDataCoincp.requests.get")
    def test_makeRequest_pass(self, mock_get):

        # @fn test_makeRequest_pass
        # tests a pass request, mocks requests.get call and returns an expected json
        # Expected return from tested method is a json

        func = "assets"
        params = {"payload": "bictoin", "limit": 1}

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

        ret = self.mktApi._makeRequest(baseUrl=func, params=params)

        self.assertTrue(mock_get.called)
        self.assertIsInstance(ret, dict)

    def test_getInterval_notTuple(self):

        # @fn test_getInterval_notTuple
        # Test that calls _getInterval with an argument that is not a tuple Should retunr False

        interval = "1,m"


        self.assertRaises(BadKwargs, self.mktApi._getIntvl, interval)

    def test_getInterval_notsupported(self):

        # @fn test_getInterval_notsupported
        # Test that _

        interval = (1, "b")

        self.assertRaises(BadKwargs, self.mktApi._getIntvl, interval)
        
    def test_getInterval_pass(self):

        # @fn test_getInterval_notsupported
        # Test that _

        interval = (1, "m")

        res = self.mktApi._getIntvl(interval)

        self.assertIsInstance(res, str)
        self.assertEqual(res, "m1")


    @patch("tradingBot.mktDataModule.mktDataCoincp.mktDataBaseCoincp._makeRequest")
    def test_getCurData_makeRequest_fail(self, mock_makeRequest):

        # @fn test_getCurData_Not_sufficient_kwargs
        # Test that fails the make request method by either fail response or no calling the method

        coin = "ETH"
        pair = "BTC"

        mock_makeRequest.return_value = False

        res = self.mktApi.getCurData(coin=coin, pair=pair)

        self.assertFalse(res)
        self.assertTrue(mock_makeRequest.called)

    @patch("tradingBot.mktDataModule.mktDataCoincp.mktDataBaseCoincp._makeRequest")
    def test_getCurData_pass(self, mock_makeRequest):

        # @fn test_getCurData_Not_sufficient_kwargs
        # Test that fails the make request method by either fail response or no calling the method

        coin = "ETH"
        pair = "USDT"

        mock_makeRequest.return_value = {
            "data": [
                {
                    "exchangeId": "binance",
                    "rank": "3",
                    "baseSymbol": "ETH",
                    "baseId": "ethereum",
                    "quoteSymbol": "USDT",
                    "quoteId": "united-states-dollar",
                    "priceQuote": "474.1200000000000000",
                    "priceUsd": "474.1200000000000000",
                    "volumeUsd24Hr": "26469866.2391238204000000",
                    "percentExchangeVolume": "6.4601522263980927",
                    "tradesCount24Hr": "12460",
                    "updated": 1605812915525
                }
            ],
            "timestamp": 1605813122180
        }

        res = self.mktApi.getCurData(coin=coin, pair=pair)

        expectedRes = {
            "exchangeId": "binance",
            "calledAPI": "coincap",
            "data": [
                {
                    "coin": coin,
                    "pair": pair,
                    "price": "474.1200000000000000",
                    "volume24Hr": "26469866.2391238204000000",
                    "percentChangeLast24": "6.4601522263980927",
                    "timestamp": 1605812915525
                }
            ]
        }

        self.assertDictEqual(res, expectedRes)

    def test_OCHLData_not_required_kwargs(self):

        # @fn test_OCHLData_not_required_kwargs
        # Test OCHLData with incomplete kwargs, i.e., not the required arguments

        coin = "BTC"
        pair = "ETH"
        self.assertRaises(BadKwargs, self.mktApi.OCHLData, coin=coin, pair=pair)


    @patch("tradingBot.mktDataModule.mktDataCoincp.mktDataBaseCoincp._makeRequest")
    def test_OCHLData_makeRequest_fail(self, mock_makeRequest):
        coin = "BTC"
        pair = "ETH"
        interval = (1, "d")

        mock_makeRequest.return_value = False

        res = self.mktApi.OCHLData(coin=coin, pair=pair, interval=interval)

        self.assertFalse(res)
        self.assertTrue(mock_makeRequest.called)

    @patch("tradingBot.mktDataModule.mktDataCoincp.mktDataBaseCoincp._makeRequest")
    def test_OCHLData_pass(self, mock_makeRequest):
        coin = "BTC"
        pair = "USDT"
        interval = (1, "d")
        expectedRes = {
            "start": 1606509660000,
            "end": 1606509660000,
            "interval": "d1",
            "calledAPI": "coincap",
            "data": [
                {
                    "open": "17072.2300000000000000",
                    "high": "17080.0000000000000000",
                    "low": "17056.9800000000000000",
                    "close": "17062.5400000000000000",
                    "volume": "54.5517220000000000",
                    "timestamp": 1606509660000
                }]
        }

        mock_makeRequest.return_value = {
            "data": [
                {
                    "open": "17072.2300000000000000",
                    "high": "17080.0000000000000000",
                    "low": "17056.9800000000000000",
                    "close": "17062.5400000000000000",
                    "volume": "54.5517220000000000",
                    "period": 1606509660000
                }]}

        res = self.mktApi.OCHLData(coin=coin, pair=pair, interval=interval)

        self.assertDictEqual(res, expectedRes)

    def test_checkCond_coin_not_found(self):

        # @fn test_checkCond_coin_not_found
        # test _checkCond method with a non existing coin

        self.assertRaises(SymbolNotSupported,
                          self.mktApi._checkCond, coin="ADA", pair="BTC")

    def test_checkCond_pair_not_found(self):

        # @fn test_checkCond_coin_not_found
        # test _checkCond method with a non existing pair

        self.assertRaises(SymbolNotSupported,
                          self.mktApi._checkCond, coin="BTC", pair="ADA")

        
    def test_checkCond_coin_found(self):

        # @fn test_checkCond_coin_not_found
        # test _checkCond method with an existing coin

        ret = self.mktApi._checkCond(coin="BTC", pair="ETH")

        self.assertTrue(ret, "Coin not found in dict")
