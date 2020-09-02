import logger as logger
from globals import globvars
import const

class Account():
    def __init__(self):
        self.data = {}
        self.idx = 0
        for x in ["Currency", "NetDividend", "NetLiquidationByCurrency", "OptionMarketValue", "RealizedPnL","TotalCashBalance"]:
            globvars.accountData[x] = [0,0,0,0,0]

    def update (self,key,value):
        globvars.logger.info("%s => %s",key,value)

        if self.idx == 4:
            self.idx = 0

        if key == "AccountCode":
            globvars.accountData[key] =  value
        elif key == "NetLiquidation":
            globvars.accountData[key] = value
        elif key == "Currency":
            globvars.accountData[key][self.idx] =  value
            self.idx =self.idx+1
        elif key == "NetDividend":
            globvars.accountData[key][self.idx] =  value
            self.idx =self.idx+1
        elif key == "NetLiquidationByCurrency":
            globvars.accountData[key][self.idx] =  value
            self.idx =self.idx+1


