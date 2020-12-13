# tests for mktDataMessari
# @author Angel Avalos 

import sys
sys.path.insert(0, r'')
from tradingBot.mktDataModule.mktData import mktDataMessari
from unittest import TestCase
from unittest.mock import patch




class TestmktDataBaseMessari(TestCase):
    # Tests Messari API
    # @class TestmktDataBaseMessari
    
    def setUp(self):

        # @fn setup
        # Creates the objet of mktDataMessari for tests

        self.mktApi = mktDataMessari()
        
    def test_getInterval_pass(self):

        # @fn test_getInterval_pass
        # Test that call _getInterval with a correct tuple format should return a string with the Messari format

        interval = (1, "m")

        res = self.mktApi._getIntvl(interval)

        self.assertIsInstance(res, str)
        self.assertEqual(res, "1m")
    
    def test_getInterval_notTuple(self):

        # @fn test_getInterval_notTuple
        # Test that call _getInterval with an argument that is not a Tuple should return False

        interval = ("1m")

        res = self.mktApi._getIntvl(interval)
        self.assertFalse(res)
    
    def test_getInterval_notsupported(self):

        # @fn test_getInterval_notTuple
        # Test that call _getInterval with an argument that is not a Tuple should return False

        interval = (1, "b")

        res = self.mktApi._getIntvl(interval)

        self.assertFalse(res)
    
    @patch("tradingBot.mktDataModule.mktDataMessari.requests.get")
    def test_makeRequest_failed(self, mock_get):

        # @fn test_makeRequest_failed
        # tests a failed request, mocks requests.get call and returns a False in response.ok

        func = "assets"
        params = {"payload": "bictoin", "limit": 1}

        mock_get.return_value.ok = False

        ret = self.mktApi._makeRequest(baseUrl=func, params=params)

        self.assertTrue(mock_get.called)
        self.assertFalse(ret, "Request was false")

    @patch("tradingBot.mktDataModule.mktDataMessari.requests.get")
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


    def test_getCurData_checkCond_fail(self):

        # @fn test_getCurData_Not_sufficient_kwargs
        # Test a call to getCurData with wrong coin or pair, Method _checkCond should fail and
        # whole method fails with False

        coin = "ADA"
        pair = None

        res = self.mktApi.getCurData(coin=coin, pair=pair)

        self.assertFalse(res)

    @patch("tradingBot.mktDataModule.mktDataMessari.mktDataBaseMessari._makeRequest")
    def test_getCurData_makeRequest_fail(self, mock_makeRequest):

        # @fn test_getCurData_Not_sufficient_kwargs
        # Test that fails the make request method by either fail response or no calling the method

        coin = "ETH"
        pair = "BTC"

        mock_makeRequest.return_value = False

        res = self.mktApi.getCurData(coin=coin, pair=pair)

        self.assertFalse(res)
        self.assertTrue(mock_makeRequest.called)

    @patch("tradingBot.mktDataModule.mktDataMessari.mktDataBaseMessari._makeRequest")
    def test_getCurData_pass(self, mock_makeRequest):

        # @fn test_getCurData_Not_sufficient_kwargs
        # Test that fails the make request method by either fail response or no calling the method

        coin = "ETH"
        pair = "USDT"

        mock_makeRequest.return_value = {
            'status': {'elapsed': 1, 'timestamp': '2020-12-12T20:10:17.629637446Z'}, 
            'data': {
                'id': '1e31218a-e44e-4285-820c-8282ee222035', 
                'symbol': 'BTC', 
                'name': 'Bitcoin', 
                'slug': 'bitcoin', 
                '_internal_temp_agora_id': '9793eae6-f374-46b4-8764-c2d224429791', 
                'market_data': {
                    'price_usd': 18787.516269557786, 
                    'price_btc': 1, 
                    'price_eth': 33.033758780867544, 
                    'volume_last_24_hours': 21541046653.29936, 
                    'real_volume_last_24_hours': 2167895311.455069, 
                    'volume_last_24_hours_overstatement_multiple': 9.936386936895596, 
                    'percent_change_usd_last_24_hours': 4.478316857197042, 
                    'percent_change_btc_last_24_hours': 0, 
                    'percent_change_eth_last_24_hours': 0.4811052880581084, 
                    'ohlcv_last_1_hour': {
                        'open': 18734.633471226873, 
                        'high': 18864.156606732628, 
                        'low': 18720.350693536977, 
                        'close': 18787.14026126218, 
                        'volume': 178416948.82255214}, 
                    'ohlcv_last_24_hour': {
                        'open': 18031.28122162749, 
                        'high': 18860.940305013737, 
                        'low': 17925.401779664964, 
                        'close': 18787.51626955779, 
                        'volume': 2512413445.480152},
                    'last_trade_at': '2020-12-12T20:10:15.623Z'
                    }
                }
            }

        res = self.mktApi.getCurData(coin=coin, pair=pair)

        expectedRes = {
            'exchangeId': None,
            'calledAPI': 'messari',
            'data': [{
                'coin': 'BTC',
                'pair': 'USDT',
                'price': 18787.516269557786,
                'volume24Hr': 21541046653.29936,
                'percentChangeLast24': 9.936386936895596,
                'timestamp': 1607800217629
                }]
            }

        self.assertDictEqual(res, expectedRes)

    def test_OCHLData_not_required_kwargs(self):

        # @fn test_OCHLData_not_required_kwargs
        # Test OCHLData with incomplete kwargs, i.e., not the required arguments

        coin = "BTC"
        pair = "ETH"

        res = self.mktApi.OCHLData(coin=coin, pair=pair)

        self.assertFalse(res)

    @patch("tradingBot.mktDataModule.mktDataMessari.mktDataBaseMessari._makeRequest")
    def test_OCHLData_makeRequest_fail(self, mock_makeRequest):
        coin = "BTC"
        pair = "ETH"
        interval = (1, "d")

        mock_makeRequest.return_value = False

        res = self.mktApi.OCHLData(coin=coin, pair=pair, interval = interval)

        self.assertFalse(res)

    @patch("tradingBot.mktDataModule.mktDataMessari.mktDataBaseMessari._makeRequest")
    def test_OCHLData_pass(self, mock_makeRequest):
        coin = "ETH"
        pair = "USDT"
        start = 1606409660000
        end = 1606509660000
        interval = (1, "day")
        expectedRes = {
            'calledAPI': 'messari',
            'start': 1606435200000,
            'end': 1606435200000,
            'interval': '1d',
            'data': [{
                'open': 519.83,
                'close': 518.68,
                'high': 530.62,
                'low': 493.72,
                'volume': 1087062.88474,
                'timestamp': 1606435200000
                }]
            }

        mock_makeRequest.return_value = {
            'status': {
                'elapsed': 3, 
                'timestamp': '2020-12-12T19:11:31.295862202Z'
                }, 
            'data': {
                'market_id': 'c8db0d97-2d3b-4206-8279-2e9ca48db163', 
                'market_name': 'binance eth-usdt', 
                'market_slug': 'binance-eth-usdt', 
                'class': 'spot', 
                'is_included_in_messari_price': True, 
                'parameters': {'start': '2020-11-26T16:54:20Z', 'end': '2020-11-27T20:41:00Z', 'interval': '1d', 'order': 'ascending', 'format': 'json', 'timestamp_format': 'unix-milliseconds', 'columns': ['timestamp', 'open', 'high', 'low', 'close', 'volume'], 'market_key': 'binance-eth-usdt', 'market_id': 'c8db0d97-2d3b-4206-8279-2e9ca48db163'}, 
                'schema': {'metric_id': 'price', 'description': 'Open, high, low, close, and volume for the market, specified in units of the quote asset', 'values_schema': {'timestamp': 'Time in milliseconds since the epoch (1 January 1970 00:00:00 UTC)', 'open': 'The price of the asset at the beginning of the specified interval in US dollars.', 'high': 'The highest price of the asset during the specified interval in US dollars.', 'low': 'The highest price of the asset during the specified interval in US dollars', 'close': 'The price of the asset at the end of the specified interval in US dollars.', 'volume': 'The total volume traded during the specified interval.'}, 'minimum_interval': '1m', 'first_available': '2017-10-27T21:49:28Z', 'last_available': None, 'source_attribution': [{'name': 'Kaiko', 'url': 'https://www.kaiko.com/'}]}, 
                'values': [[1606435200000, 519.83, 530.62, 493.72, 518.68, 1087062.88474]]
                }
            }
        
        res = self.mktApi.OCHLData(coin=coin, pair=pair, \
            start = start, end = end , interval = interval)

        self.assertDictEqual(res, expectedRes)

    def test_checkCond_coin_not_found(self):

        # @fn test_checkCond_coin_not_found
        # test _checkCond method with a non existing coin

        ret = self.mktApi._checkCond(coin="ADA", pair="BTC")

        self.assertFalse(ret, "Coin not found in dict")

    def test_checkCond_pair_not_found(self):

        # @fn test_checkCond_coin_not_found
        # test _checkCond method with a non existing pair

        ret = self.mktApi._checkCond(coin="BTC", pair="EUR")

        self.assertFalse(ret, "Pair not found in dict")

    def test_checkCond_coin_found(self):

        # @fn test_checkCond_coin_not_found
        # test _checkCond method with an existing coin

        ret = self.mktApi._checkCond(coin="BTC", pair="ETH")

        self.assertTrue(ret, "Coin not found in dict")

    def test_timeUnix_pass(self):

        # @fn test_timeUnix_pass
        # test _timeUnix method with an correct timestamp

        res = self.mktApi._timeUnix(timestamp="2020-12-12T20:10:17.629637446Z")

        self.assertEqual(res, 1607800217629)    