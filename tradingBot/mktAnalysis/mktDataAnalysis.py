import sys
sys.path.insert(0, r'')

import json
from tradingBot.mktDataModule.mktDataMessari import mktDataBaseMessari
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random


class mktDataAnalysis():
    
    getData = mktDataBaseMessari()
    paths = {"mainPath": "tradingBot\dataBase\{}\{}", "subPaths": [
        {"id": "indicators", "subPath": "\indicators\indic.json"},
        {"id": "intervals", "subPath": "\intervals\{}.json"}
    ]}
    
    def __init__(self, coin=None, pair=None):
        
        mainPath = self.paths['mainPath'].format(coin.lower(), pair.lower())
        self.indicPath = mainPath + self.paths['subPaths'][0]["subPath"]
        self.DBPath = mainPath + self.paths['subPaths'][1]["subPath"]
        self.indic = self.openInd()

    def newIndicator(self, indicator=None, period=None, interval=None):
        if not isinstance(period, int):
            return False 
        interval = self.getData._getIntvl(timeframe=interval)
        id = str(period) + indicator + interval
        for line in self.indic['indicators']:
            if line["id"] == id:
                return False
            if indicator == "RSI" and indicator == \
                    line['indicator'] and interval == line['interval']:
                return False 
        newInd = {
            "indicator": indicator,
            "interval": interval,
            "period": period,
            "id": id,
            "data": []
        }
        newInd['data'] = self.actlIndData(indicator=indicator, period=period, interval=interval)
        if not newInd['data']:
            return False
        self.indic["indicators"].append(newInd)
        self.closeInd(indic=self.indic)      

    def delIndicator(self, id=None):
        newInd = {"indicators": []}
        for line in self.indic['indicators']:
            if not line["id"] == id:
                newInd["indicators"].append(line)
        self.indic = newInd
        self.closeInd(indic=newInd)                     

    def actlIndicators(self):
        for ind in self.indic['indicators']:
            ind['data'] = self.actlIndData(indicator=ind['indicator'], \
                period=ind['period'], interval=ind['interval'])
        self.closeInd(indic=self.indic)  

    def actlIndData(self, indicator=None, period=None, interval=None):
        if "EMA" == indicator:
            data = self.indEMA(period=period, interval=interval)
        elif "RSI" == indicator:
            data = self.indRSI(period=period, interval=interval)      
        elif "SMA" == indicator:
            data = self.indSMA(period=period, interval=interval)     
        elif "WMA" == indicator:
            data = self.indWMA(period=period, interval=interval)        
        else:
            return False
        return data
    
    def viewIndicators(self):
        indica = {"indicators": []}
        for line in self.indic['indicators']:
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
        
    def indRSI(self, period=None, interval=None):
        data = self.openDB(interval=interval)
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
        return actData

    def indEMA(self, period=None, interval=None):
        data = self.openDB(interval=interval)
        ema = data['close'].ewm(span=period).mean()
        
        actData = pd.DataFrame()
        actData['timestamp'] = data['timestamp']
        actData['value'] = ema
        actData = json.loads(actData.to_json(orient="records"))
        return actData

    def indSMA(self, period=None, interval=None):
        data = self.openDB(interval=interval)
        sma = data['close'].rolling(window=period).mean()

        actData = pd.DataFrame()
        actData['timestamp'] = data['timestamp']
        actData['value'] = sma
        actData = json.loads(actData.to_json(orient="records"))
        return actData

    def indWMA(self, period=None, interval=None):
        def wma_calc(w):
            def g(x):
                return sum(w * x) / sum(w)
            return g  

        weights = list(reversed([(period - n) * period for n in range(period)]))
        data = self.openDB(interval=interval)
        wma = data['close'].rolling(window=period).apply(wma_calc(weights), raw=True)

        actData = pd.DataFrame()
        actData['timestamp'] = data['timestamp']
        actData['value'] = wma
        actData = json.loads(actData.to_json(orient="records"))
        return actData
    
    def actlDB(self, interval=None, start=None, end=None):
        if end == None:
            today = datetime.datetime.now()
            today = int(today.timestamp() * 1000)
            end = today
        data = self.getData.OCHLData(coin="BTC", pair="USDT", start=start, end=end, interval=interval)
        interval = self.getData._getIntvl(timeframe=interval)
        with open(self.DBPath.format(interval), 'w') as f:
            json.dump(data, f, indent=2)
    
    def openDB(self, interval=None):
        with open(self.DBPath.format(interval), 'r') as f:
            data = json.load(f)
        data = pd.DataFrame.from_dict(data["data"], orient='columns')
        return data
    
    def openInd(self):
        with open(self.indicPath, 'r') as f:
            indic = json.load(f)
        return indic
    
    def closeInd(self, indic=None):
        with open(self.indicPath, 'w') as f:
            json.dump(indic, f, indent=1) 
    
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

        for ind in self.indic['indicators']:
            indData = pd.DataFrame.from_dict(ind["data"], orient='columns')
            if ind['interval'] == interval:
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
      
    y = mktDataAnalysis(coin="BTC", pair="USDT")
    y.delIndicator(id="15WMA1h")
    y.newIndicator(indicator="WMA", period=15, interval=(1, "hour"))
    y.actlIndicators()
    y.viewIndicators()
    #y.printGraph(interval=(1, "day"))
    #y.actlDB(interval=(1, "hour"))
    