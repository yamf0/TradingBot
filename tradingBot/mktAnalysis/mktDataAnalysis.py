import sys
sys.path.insert(0, r'')

import json
import os
from tradingBot.mktDataModule.mktDataMessari import mktDataBaseMessari
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random


class mktDataAnalysis():
    
    getData = mktDataBaseMessari()
    paths = {"mainPath": "tradingBot\dataBase\{}\{}", "subPaths": [
        {"id": "indicators", "subPath": "\indicators"},
        {"id": "intervals", "subPath": "\intervals"}
    ]}
    
    def __init__(self, coin=None, pair=None, indicators=None):
        
        mainPath = self.paths['mainPath'].format(coin.lower(), pair.lower())
        self.indicPath = mainPath + self.paths['subPaths'][0]["subPath"]
        self.DBPath = mainPath + self.paths['subPaths'][1]["subPath"]
        self.getIndInterval = []
        self.openInd()
        for indic in indicators:
            self.newIndicator(indicator=indic["indicator"], period=indic["period"],\
                interval=indic["interval"])

    def newIndicator(self, indicator=None, period=None, interval=None):
        if not isinstance(period, int):
            return False 
        interval = self.getData._getIntvl(timeframe=interval)
        id = str(period) + indicator + interval        
        for indicFiles in self.getIndInterval:
            indicInterval = getattr(self, indicFiles["indicator_int"])
            for line in indicInterval['indicators']:
                if line["id"] == id:
                    return False
                if indicator == "RSI" and indicator == \
                        line['indicator'] and interval == line['interval']:
                    return False 
        if not self.checkIntDB(interval=interval):
            return False
        newInd = {
            "indicator": indicator,
            "interval": interval,
            "period": period,
            "id": id,
            "start": 0,
            "end": 0,
            "data": []
        }
        newInd['data'] = self.actlIndData(indicator=indicator, period=period, interval=interval,\
            start=None, end=None, int_unix=None)
        if not newInd['data']:
            return False
        newInd['start'] = newInd['data'][0]['timestamp']
        newInd['end'] = newInd['data'][-1]['timestamp']
        indic = getattr(self, "indic_" + interval)
        indic["indicators"].append(newInd)
        setattr(self, "indic_" + interval, indic)
        self.closeInd()      

    def delIndicator(self, id=None):
        for indicFiles in self.getIndInterval:
            newInd = {"indicators": []}
            indicInterval = getattr(self, indicFiles["indicator_int"])
            for line in indicInterval['indicators']:
                if not line["id"] == id:
                    newInd["indicators"].append(line)
            setattr(self, indicFiles["indicator_int"], newInd)
        self.closeInd()                     

    def delAllIndicator(self):
        for indicFiles in self.getIndInterval:
            newInd = {"indicators": []}
            setattr(self, indicFiles["indicator_int"], newInd)
        self.closeInd() 

    def actlIndicators(self):
        for indicFiles in self.getIndInterval:
            newInd = {"indicators": []}
            indicInterval = getattr(self, indicFiles["indicator_int"])
            for line in indicInterval['indicators']:
                info = {
                    "indicator": line['indicator'],
                    "interval": line['interval'],
                    "period": line['period'],
                    "id": line['id'],
                    "start": line['data'][0]['timestamp'],
                    "end": line['data'][-1]['timestamp'],
                    "data": line['data']
                }
                int_unix = info['data'][1]['timestamp'] - info['data'][0]['timestamp']
                newData = self.actlIndData(indicator=info['indicator'], period=info['period'],\
                    interval=info['interval'], start=info['start'], end=info['end'], int_unix=int_unix)
                if newData[0]['timestamp'] == info['end']:
                    info['data'][-1] = newData[0]
                else:
                    del info['data'][0:len(newData)]
                    info['data'] += newData
                info['start'] = info['data'][0]['timestamp']
                info['end'] = info['data'][-1]['timestamp']                
                newInd["indicators"].append(info)
            setattr(self, indicFiles["indicator_int"], newInd)
        self.closeInd()  

    def actlIndData(self, indicator=None, period=None, interval=None, start=None, end=None, int_unix=None):
        if "EMA" == indicator:
            data = self.indEMA(period=period, interval=interval, start=start, end=end, int_unix=int_unix)
        elif "RSI" == indicator:
            data = self.indRSI(period=period, interval=interval, start=start, end=end, int_unix=int_unix)      
        elif "SMA" == indicator:
            data = self.indSMA(period=period, interval=interval, start=start, end=end, int_unix=int_unix)     
        elif "WMA" == indicator:
            data = self.indWMA(period=period, interval=interval, start=start, end=end, int_unix=int_unix)        
        else:
            return False
        return data
    
    def viewIndicators(self):
        indica = {"indicators": []}
        for indicFiles in self.getIndInterval:
            indicInterval = getattr(self, indicFiles["indicator_int"])
            for line in indicInterval['indicators']:
                newInd = {
                    "indicator": line['indicator'],
                    "interval": line['interval'],
                    "period": line['period'],
                    "id": line['id'],
                }            
                indica["indicators"].append(newInd)
        data = pd.DataFrame.from_dict(indica['indicators'], orient='columns')
        data = data.sort_values(by=['interval', 'indicator', 'period'])
        data = data.reindex(columns=['interval', 'indicator', 'period', 'id'])
        print(data.to_string(index=False))
        
    def indRSI(self, period=None, interval=None, start=None, end=None, int_unix=None):
        def calcData(data=None, kLines=None):
            delta = data['close'].diff(1)
            delta.dropna(inplace=True)
            positive = delta.copy()
            negative = delta.copy()
            positive[positive < 0] = 0
            negative[negative > 0] = 0
            average_gain = positive.rolling(window=period).mean()
            average_loss = abs(negative.rolling(window=period).mean())
            relative_strength = average_gain / average_loss
            rsi = 100.0 - (100.0 / (1.0 + relative_strength))

            actData = pd.DataFrame()
            actData['timestamp'] = data['timestamp']
            actData['value'] = rsi
            actData = json.loads(actData.to_json(orient="records"))
            return actData[kLines:]

        data = self.openDB(interval=interval)
        startDB = data.iloc[0]['timestamp']
        endDB = data.iloc[-1]['timestamp']        
        if int_unix == None or end > data.iloc[-1]['timestamp']:
            actData = calcData(data=data, kLines=0)
        elif end == endDB: 
            actData = calcData(data=data[-(period + 1):], kLines=-1)
        else:
            opData, kLines = self.checkLen(period=period, end=end, endDB=endDB, int_unix=int_unix)
            actData = calcData(data=data[opData:], kLines=kLines)
        return actData

    def indEMA(self, period=None, interval=None, start=None, end=None, int_unix=None):
        def calcData(data=None, kLines=None):
            ema = data['close'].ewm(span=period).mean()
            
            actData = pd.DataFrame()
            actData['timestamp'] = data['timestamp']
            actData['value'] = ema
            actData = json.loads(actData.to_json(orient="records"))
            return actData[kLines:]

        data = self.openDB(interval=interval)
        startDB = data.iloc[0]['timestamp']
        endDB = data.iloc[-1]['timestamp']        
        if int_unix == None or end > data.iloc[-1]['timestamp']:
            actData = calcData(data=data, kLines=0)
        elif end == endDB: 
            actData = calcData(data=data[-(period + 1):], kLines=-1)
        else:
            opData, kLines = self.checkLen(period=period, end=end, endDB=endDB, int_unix=int_unix)
            actData = calcData(data=data[opData:], kLines=kLines)
        return actData

    def indSMA(self, period=None, interval=None, start=None, end=None, int_unix=None):
        def calcData(data=None, kLines=None):
            sma = data['close'].rolling(window=period).mean()
            
            actData = pd.DataFrame()
            actData['timestamp'] = data['timestamp']
            actData['value'] = sma
            actData = json.loads(actData.to_json(orient="records"))            
            return actData[kLines:]

        data = self.openDB(interval=interval)
        startDB = data.iloc[0]['timestamp']
        endDB = data.iloc[-1]['timestamp']
        if int_unix == None or end > data.iloc[-1]['timestamp']:
            actData = calcData(data=data, kLines=0)
        elif end == endDB: 
            actData = calcData(data=data[-(period + 1):], kLines=-1)
        else:
            opData, kLines = self.checkLen(period=period, end=end, endDB=endDB, int_unix=int_unix)
            actData = calcData(data=data[opData:], kLines=kLines)
        return actData

    def indWMA(self, period=None, interval=None, start=None, end=None, int_unix=None):
        def calcData(data=None, kLines=None):
            wma = data['close'].rolling(window=period).apply(wma_calc(weights), raw=True)

            actData = pd.DataFrame()
            actData['timestamp'] = data['timestamp']
            actData['value'] = wma
            actData = json.loads(actData.to_json(orient="records"))
            return actData[kLines:]

        def wma_calc(w):
            def g(x):
                return sum(w * x) / sum(w)
            return g  

        weights = list(reversed([(period - n) * period for n in range(period)]))
        data = self.openDB(interval=interval)
        startDB = data.iloc[0]['timestamp']
        endDB = data.iloc[-1]['timestamp']        
        if int_unix == None or end > data.iloc[-1]['timestamp']:
            actData = calcData(data=data, kLines=0)
        elif end == endDB:  
            actData = calcData(data=data[-(period + 1):], kLines=-1)
        else:
            opData, kLines = self.checkLen(period=period, end=end, endDB=endDB, int_unix=int_unix)
            actData = calcData(data=data[opData:], kLines=kLines)
        return actData
    
    def checkLen(self, period=None, end=None, endDB=None, int_unix=None):
        kLines = -((endDB - end) / int_unix)
        opData = kLines - period - 1   
        kLines = int(kLines)
        opData = int(opData)
        return opData, kLines

    def actlDB(self, interval=None, start=None, end=None):
        if end == None:
            today = datetime.datetime.now()
            today = int(today.timestamp() * 1000)
            end = today
        data = self.getData.OCHLData(coin="BTC", pair="USDT", start=start, end=end, interval=interval)
        interval = self.getData._getIntvl(timeframe=interval)
        with open(self.DBPath + "\{}.json".format(interval), 'w') as f:
            json.dump(data, f, indent=2)
    
    def openDB(self, interval=None):
        with open(self.DBPath + "\{}.json".format(interval), 'r') as f:
            data = json.load(f)
        data = pd.DataFrame.from_dict(data["data"], orient='columns')
        return data
    
    def openInd(self):
        for rooth_path, sub_path, files in os.walk(self.indicPath):
            for indicFiles in files:
                indic = self.indicPath + "\{}".format(indicFiles)
                with open(indic, 'r') as f:
                    data = json.load(f)  
                setattr(self, indicFiles[:-5], data)
                getIndic = {"indicator_int": indicFiles[:-5], "interval": indicFiles[6:-5], "path": indicFiles}
                self.getIndInterval.append(getIndic)

    def closeInd(self):
        for indicFiles in self.getIndInterval:
            indic = self.indicPath + "\{}".format(indicFiles["path"])
            indicInterval = getattr(self, indicFiles["indicator_int"])
            with open(indic, 'w') as f:
                json.dump(indicInterval, f, indent=1) 
    
    def checkIntDB(self, interval=None):
        flag = False
        bool1 = True
        newInd = {"indicators": []}
        for rooth_path, sub_path, files in os.walk(self.DBPath):
            for intervals in files:
                if intervals[:-5] == interval: flag = True 
        if flag:
            for intervals in self.getIndInterval:
                if intervals["interval"] == interval: bool1 = False                 
        else: return flag
        if bool1:
            getIndic = {"indicator_int": "indic_{}".format(interval),\
                "interval": interval, "path": "indic_{}.json".format(interval)}
            self.getIndInterval.append(getIndic)
            setattr(self, "indic_{}".format(interval), newInd)
            return True
        else: return True

    def printGraph(self, interval=None):
        def randColor(x):
            colors = ("red", "blue", "green", "orange", "yellow", "pink", "olive", \
                "brown", "lime", "crimson", "aqua", "powderblue", "palegreen")
            #r = random.random() 
            #b = random.random() 
            #g = random.random()            
            #color = (r, g, b) 
            color = colors[x]
            return color
        interval = self.getData._getIntvl(timeframe=interval)
        data = self.openDB(interval=interval)
        flag = False
        x = 0
        plt.figure(figsize=(12, 8))
        ax1 = plt.subplot(211)
        ax1.plot(data['timestamp'], data['close'], color='lightgray', label='Price USD')
        indic = getattr(self, "indic_" + interval)
        for ind in indic['indicators']:
            indData = pd.DataFrame.from_dict(ind["data"], orient='columns')
            if ind['indicator'] == "RSI":
                indRSIData = indData
                indRSIPeriod = str(ind['period'])
                flag = True
            else:
                ax1.plot(indData['timestamp'], indData['value'], linestyle='--', \
                    color=randColor(x), label=ind['indicator'] + " " + str(ind['period']))
                x += 1
     
        ax1.set_title("BTC Price USD. Interval: " + interval, color='white')
        ax1.legend()
        ax1.grid(True, color="#555555")
        ax1.set_axisbelow(True)
        ax1.set_facecolor("black")
        ax1.figure.set_facecolor("#121212")
        ax1.tick_params(axis="x", colors="white")
        ax1.tick_params(axis="y", colors="white")

        if flag == True:
            ax2 = plt.subplot(212, sharex=ax1)
            ax2.plot(indRSIData['timestamp'], indRSIData['value'], color="lightgray")
            ax2.axhline(0, linestyle='--', alpha=0.5, color='#ff0000')
            ax2.axhline(10, linestyle='--', alpha=0.5, color='#ffaa00')
            ax2.axhline(20, linestyle='--', alpha=0.5, color='#00ff00')
            ax2.axhline(30, linestyle='--', alpha=0.5, color='#cccccc')
            ax2.axhline(70, linestyle='--', alpha=0.5, color='#cccccc')
            ax2.axhline(80, linestyle='--', alpha=0.5, color='#00ff00')
            ax2.axhline(90, linestyle='--', alpha=0.5, color='#ffaa00')
            ax2.axhline(100, linestyle='--', alpha=0.5, color='#ff0000')
            ax2.set_title("RSI Value" + " " + indRSIPeriod, color="white")
            ax2.grid(False)
            ax2.set_axisbelow(True)
            ax2.set_facecolor("black")
            ax2.tick_params(axis="x", colors="white")
            ax2.tick_params(axis="y", colors="white")

        plt.show()        


if __name__ == "__main__":
      
    y = mktDataAnalysis(coin="BTC", pair="USDT", indicators=[
        {"indicator": "EMA", "period": 17, "interval": (1, "day")},
        {"indicator": "RSI", "period": 17, "interval": (1, "day")},
        {"indicator": "SMA", "period": 17, "interval": (1, "day")},
        {"indicator": "WMA", "period": 17, "interval": (1, "day")},
        {"indicator": "EMA", "period": 17, "interval": (1, "hour")},
        {"indicator": "RSI", "period": 17, "interval": (1, "hour")},
        {"indicator": "SMA", "period": 17, "interval": (1, "hour")},
        {"indicator": "WMA", "period": 17, "interval": (1, "hour")}
    ])
    y.delIndicator(id="100WMA1h")
    y.newIndicator(indicator="WMA", period=100, interval=(1, "hour"))
    y.actlIndicators()
    y.viewIndicators()
    #y.printGraph(interval=(1, "day"))
    #y.actlDB(interval=(1, "hour"))
    #y.delAllIndicator()
    