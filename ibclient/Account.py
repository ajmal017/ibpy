import logger as logger
from globals import globvars
import const

class Account():
    def __init__(self):
        self.data = {}
        for x in ["Currency", "NetDividend", "NetLiquidationByCurrency", "OptionMarketValue", "RealizedPnL","TotalCashBalance"]:
            globvars.accountData[x] = []

    def update (self,key,value):
        globvars.logger.info("%s => %s",key,value)
        if key == "AccountCode":
            globvars.accountData[key] =  value
        elif key == "Currency":
            globvars.accountData[key].append( value )
        elif key == "NetDividend":
            globvars.accountData[key].append( value )
        elif key == "NetLiquidationByCurrency":
            globvars.accountData[key].append( value )


