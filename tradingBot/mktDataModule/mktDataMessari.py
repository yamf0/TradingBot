# @package mktDataMessari
# mktData implementation for Messari API, based in mktData interface
# @author Angel Avalos with the big support of Yael Martinez


import datetime
import requests
import sys
sys.path.insert(0, r'')

# TODO import a file containing all available coins // all available fiats

from tradingBot.mktDataModule.mktDataINF import mktDataINF
from tradingBot.resources.globals import symbolMap


class mktDataBaseMessari(mktDataINF):
    # Messari class
    # @class mktDataBaseMessari
    # @see mktDataINF

    def __init__(self):
        pass

    def _makeRequest(self, baseUrl=None, params=None):

        # @fn _makeRequest
        # @brief Method that uses requests.get() call to request the API for information
        # @param baseUrl API function to be called
        # @param params Parameters to pass with the request
        # @exception EXCEPTION response not OK
        # @return response  resonse object json

        response = requests.get(baseUrl, params)

        if not response.ok:
            # TODO Make logger message critical failed request
            # TODO RAISE ERROR
            print(response.json())
            return False

        return response.json()

    def checkConnection(self):

        # @fn checkConnection
        # @brief Method that sends a generic message to the API server to check for connection
        # @return boolean

        baseUrl = "https://data.messari.io/api/v1/assets/eth/metrics/market-data"
        params = None

        #! SHOULD I PUT IT IN A TRY EXCEPT BLOCK???
        res = self._makeRequest(baseUrl, params)

        if not res:
            # TODO Logger connection with server down
            return False

        # TODO Make logger message server connected
        return True

    def _getIntvl(self, timeframe=None):

        # @fn _getIntvl
        # @brief Method that constructs in the correct way the interval needed for the API
        # @param timeframe which time frame the data is to be obtained (e.g. (1, "min")//(1, "day"))
        # @return interval constructed as a letter and the number (e.g., 1d = 1 day)

        if not isinstance(timeframe, tuple):
            # TODO RAISE ERROR TIME FRAME IS NOT A TUPLE
            return False

        number, timeInterval = timeframe
        if timeInterval[0] not in "mhwd":
            # TODO RAISE ERROR TimeInterval not in defined intervals
            return False
        timeInterval = timeInterval[0]

        return str(number) + timeInterval

    def _checkCond(self, **kwargs):

        # @fn _checkCond
        # @brief Method that checks that coin Conditions are met
        #         Coin requested does exists, pair requested does exist.
        # @param coin coin requested
        # @param pair pair requested
        # @exception EXCEPTION coin//pair not in available coins
        # @return boolean

        coin, pair, *_ = [kwargs[key] for key in kwargs.keys()]

        if coin not in [crypto["symbol"] for crypto in symbolMap["crypto"]]:
            # TODO RAISE ERROR COIN REQUESTED NOT IN AVAILABLE COINS
            return False
        if pair is None:
            pass
        else:
            if pair not in [crypto["symbol"] for crypto in symbolMap["crypto"]] + \
                    [fiat["symbol"] for fiat in symbolMap["fiat"]]:
                # TODO RAISE ERROR PAIR REQUESTED NOT IN AVAILABLE COINS
                return False
        return True

    def _parseResponse(self, func=None, info=None):

        # @fn _parseResponse
        # @brief Method that parse the response in a defined json structure
        # @param func the type of json to be parsed
        # @param info json to be parsed
        # @return res the json produced

        calledAPI = "messari"
        if func == "getCurData":
            data = info["data"]
            exchange = None
            coin = data["symbol"]
            pair = "USDT"
            data = data["market_data"]
            price = data["price_usd"]
            volume24Hr = data["volume_last_24_hours"]
            percentChangeLast24 = data["volume_last_24_hours_overstatement_multiple"]
            timestamp = self._timeUnix(info["status"]["timestamp"])

            res = {
                "exchangeId": exchange,
                "calledAPI": calledAPI,
                "data": [
                    {
                        "coin": coin,
                        "pair": pair,
                        "price": price,
                        "volume24Hr": volume24Hr,
                        "percentChangeLast24": percentChangeLast24,
                        "timestamp": timestamp
                    }
                ]
            }

            return res
        elif func == "OCHLData":
            res = {
                "calledAPI": calledAPI,
                "start": "",
                "end": "",
                "interval": "",
                "data": []
            }
            data = info["data"]["values"]
            for d in data:

                dDict = {
                    "open": d[1],
                    "close": d[4],
                    "high": d[2],
                    "low": d[3],
                    "volume": d[5],
                    "timestamp": d[0]
                }
                res["data"].append(dDict)
            res["start"] = res["data"][0]["timestamp"]
            res["end"] = res["data"][-1]["timestamp"]

            return res

    def _timeUnix(self, timestamp=None):

        # @fn _timeUnix
        # @brief Method that transforms the timestamp to a UNIX format
        # @param timestamp The timestamp in the default Messari format
        # @return timeUnix Timestamp in Unix format with 13 digits

        x = datetime.datetime.strptime(timestamp[:-4], '%Y-%m-%dT%H:%M:%S.%f')
        timeUnix = int(x.timestamp() * 1000)
        return timeUnix

    def getCurData(self, **kwargs):

        # @fn getCurData
        # @brief Method that gets the current price of a coin compared to pair
        #
        # Uses method _makeRequest and _cehckCond
        #
        # @param coin which coin price to obtain (e.g. BTC // ETH)
        # @see _makeRequest, _checkCond
        # @return json with the information obtained

        methodVar = {"coin": None, "exchange": "binance"}

        methodVar.update(kwargs)

        coin, exchange, *_ = [methodVar[key] for key in methodVar.keys()]

        if not self._checkCond(coin=coin, pair=None):
            return False

        # build baseUrl
        params = None
        baseUrl = "https://data.messari.io/api/v1/assets/" + \
            coin.lower() + "/metrics/market-data"
        res = self._makeRequest(baseUrl, params)

        if not res:
            # TODO Logger connection with server down
            return False

        parsedInf = self._parseResponse(func="getCurData", info=res)

        # TODO Make logger message server connected
        return parsedInf

    def _timeStamp(self, timestamp):

        # @fn _timeStamp
        # @brief Method that transforms the start and end timestamp into the format Messari requires
        # @param timestamp The timestamp in a tupple format (e.g. (10, 8, 2020) -->
        #                                 10th of AUG of 2020 (day, month, year))
        # @return timestamp Timestamp in string format (e.g. "2020-8-10" -->
        #                                 10th of AUG of 2020 "Year-Month-Day")

        if timestamp is None:
            timestamp = None
        else:
            timeS = ""
            for d in tuple(reversed(timestamp)):
                timeS += str(d) + "-"
            timestamp = timeS[:-1]
        return timestamp

    def OCHLData(self, **kwargs):

        # @fn OCHLData
        # @brief Method that gets the OCHL data for a specific coin in a specified interval
        #
        # Uses method _makeRequest and _cehckCond
        #
        # @param coin which coin price to obtain (e.g. BTC // ETH)
        # @param pair which pair coin to obtain the price for (e.g. USDT // EUR)
        # @param interval which time frame the data is to be obtained (e.g. (1, "min")//(1, "hour") //(1, "day")//(1, "week"))
        # @param start (optional) timestamp from which data starts (e.g. (10, 8, 2020) -->
        #                                 10th of AUG of 2020 (day, month, year))
        # @param end (optional) timestamp until which data ends (e.g. (10, 8, 2020) -->
        #                                 10th of AUG of 2020 (day, month, year))
        #
        # @exception EXCEPTION time interval is not permited
        # @return json with the information obtained

        methodVar = {"coin": None, "pair": None, "exchange": "binance",
                     "interval": None, "start": None, "end": None}

        methodVar.update(kwargs)

        coin, pair, exchange, interval, start, end, * \
            _ = [methodVar[key] for key in methodVar.keys()]
        
        timeframe = interval            
        #start = self._timeStamp(start)
        #end = self._timeStamp(end)

        timeframe = self._getIntvl(timeframe)
        if not timeframe:
            # TODO RAISE ERROR TimeInterval not in defined intervals
            return False

        if not self._checkCond(coin=coin, pair=pair):
            return False

        #!build baseUrl
        baseUrl = "https://data.messari.io/api/v1/markets/" + \
            exchange.lower() + "-" + coin.lower() + "-" + pair.lower() + "/metrics/price/time-series"
        params = {"start": start, "end": end, "interval": timeframe}

        res = self._makeRequest(baseUrl, params)

        if not res:
            # TODO Logger connection with server down
            return False

        parsedInf = self._parseResponse(func="OCHLData", info=res)
        parsedInf["interval"] = timeframe

        # TODO Make logger message server connected
        return parsedInf


if __name__ == "__main__":

    o = mktDataBaseMessari()
    o.checkConnection()
    o.getCurData(coin="BTC", pair="USDT")
    o.OCHLData(coin="ETH", pair="USDT", start=1606409660000,
               end=1606509660000, interval=(1, "day"))
