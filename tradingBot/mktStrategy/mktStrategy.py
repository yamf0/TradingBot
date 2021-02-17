# @package mktStrategy
# mktDataAnalysis class in charge of analysing the indicators and price for building a buying/sale strategy
# @author Angel Avalos

import sys
sys.path.insert(0, r'')

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class mktStrategy ():

    def __init__(self, coin=None, pair=None, coinBotObj=None, dataAnalysisObj=None):
        self.coinBotObj = coinBotObj
        self.dBIntervals = coinBotObj.tmfrmVar 
        self.dataAnalysisObj = dataAnalysisObj
        self.getIndInterval = dataAnalysisObj.getIndInterval
        for nameDB in self.dBIntervals:
            setattr(self, nameDB, getattr(self.coinBotObj, nameDB))
        for indicFiles in self.getIndInterval:
            setattr(self, indicFiles["indicator_int"], getattr(self.dataAnalysisObj, indicFiles["indicator_int"]))
    
    def test(self):
        print(self.indic_1h["indicators"][0]["data"][-1])
        i = 0
        for nameDB in self.dBIntervals:
            if i == 0:
                data = getattr(self, nameDB)
                print(data["data"][-1])
                i += 1
        