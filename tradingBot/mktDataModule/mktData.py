##
# mktData API classes
#@author Yael Mtz & Angel Avalos
from tradingBot.mktDataModule.mktDataCoincp import mktDataBaseCoincp
from tradingBot.mktDataModule.mktDataMessari import mktDataBaseMessari


class mktDataCoincp(mktDataBaseCoincp):

    ##@fn mktDataCoincp
    # inherits from mktDataBaseCoincp
    # @see mktDataBaseCoincp
    
    def __init__(self):

        super().__init__()


class mktDataMessari(mktDataBaseMessari):
    
    ##@fn mktDataMessari
    # inherits from mktDataBaseMessari
    # @see mktDataBaseMessari

    def __init__(self):

        super().__init__()
