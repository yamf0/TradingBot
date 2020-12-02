## @package exceptions
# Contains the custom exceptions
#@author Yael Martinez

#errors:
# _getInterval time interval not a tuple
# _getInterval time interval not in permitted intervals
# _checkCond coin not in dict
# _checkCond pair not in dict

class BadKwargs(Exception):

    def __init__(self, message):
        if message:
            self.message = message[0]
        else:
            self.message = None
        pass
    def __str__(self):
        
        return "BadKwargs, {}".format(self.message)

class SymbolNotSupported(Exception):
    
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return "SymbolNotSupported, {} symbol is not in supported"
