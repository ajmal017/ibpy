import logger as logger
from datetime import datetime
from globals import globvars
import const

class Account():
    def __init__(self):
        self.data = {}
        self.idx = {}
        self.updateCounter = 0
        self.accountData = {}
        self.accountData["AccountCode"] = ""
        self.accountData["NetLiquidation"] = ""
        self.accountData["FullInitMarginReq"] = ""
        self.accountData["lastUpdate"] = ""

        for x in ["Currency", "NetDividend", "NetLiquidationByCurrency", "OptionMarketValue", "RealizedPnL","TotalCashBalance"]:
            self.accountData[x] = [0,0,0,0,0]
            self.idx[x] = 0

    def getLastUpdateTimestamp(self):
        if "lastUpdate" in self.accountData:
            return self.accountData["lastUpdate"]

    def update (self,key,value):
        globvars.logger.info("%s => %s",key,value)
        self.accountData["lastUpdate"] = datetime.now().strftime("%H:%M:%S")

        if key == "AccountCode":
            self.accountData[key] =  value
        elif key == "NetLiquidation":
            self.updateCounter += 1
            self.accountData[key] = value
        elif key == "FullInitMarginReq":
            self.accountData[key] =  value
        elif key == "Currency":
            if self.idx[key] == 4:
                self.idx[key] = 0
            self.accountData[key][self.idx[key]] =  value
            self.idx[key] += 1
        elif key == "NetDividend":
            if self.idx[key] == 4:
                self.idx[key] = 0
            self.accountData[key][self.idx[key]] =  value
            self.idx[key] += 1
        elif key == "NetLiquidationByCurrency":
            if self.idx[key] == 4:
                self.idx[key] = 0
            self.accountData[key][self.idx[key]] =  value
            self.idx[key] += 1
