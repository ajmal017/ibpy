import datetime

import matplotlib.dates as mdates

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import ContractDetails

from Misc.globals import globvars
from Misc import const
from Model.Account import Account

from Logs import logger as logger

class BrkApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.apiLogger = logger.initApiLogger()
        self.endflag = {}
        self.histdata = {}
        self.statusbar =  None

    def setAccount(self, act):
        self.account = act

    def setBwData(self,td):
        self.buyWrites = td

    def setStatusBar(self, sb):
        self.statusbar = sb

    def eDisconnect(self):
        Close()

    def error(self, reqId: int, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)

    def getHistData(self, ti: int):
        return self.histdata[ti]

    def resetHistData(self, reqId: int):
        if reqId not in self.histdata:
            self.histdata[reqId] = []

    def historicalData(self, reqId, bar):
        tickerId = str(reqId)
        bw = self.buyWrites[tickerId]
        self.apiLogger.info("ticker: %s/%s: %s", tickerId, bw.statData.buyWrite["underlyer"]["@tickerSymbol"], str(bar.close))
        if reqId not in self.histdata:
            self.histdata[reqId] = []

        if reqId % 2 == 0:
            if len(bar.date) == 8:
                bar.date = mdates.date2num(datetime.datetime.strptime(bar.date + " 00:00:00", "%Y%m%d %H:%M:%S"))
            else:
                bar.date = mdates.date2num(datetime.datetime.strptime(bar.date, "%Y%m%d %H:%M:%S"))

            bw.set_stk_price(bar.close)
        else:
            if len(bar.date) == 8:
                bar.date = mdates.date2num(datetime.datetime.strptime(bar.date + " 00:00:00", "%Y%m%d %H:%M:%S"))
            else:
                bar.date = mdates.date2num(datetime.datetime.strptime(bar.date, "%Y%m%d %H:%M:%S"))
            bw.set_opt_price(bar.close)


        self.histdata[reqId].append([bar.date, bar.open, bar.high, bar.low, bar.close])

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        if reqId not in self.endflag:
            self.endflag[reqId] = False
        super().historicalDataEnd(reqId, start, end)
        # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.endflag[reqId] = True

    def historicalDataUpdate(self, reqId: int, bar):
         print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        tickerId = str(reqId)

        bw = self.buyWrites[tickerId]

        super().contractDetails(reqId, contractDetails)
        industry = contractDetails.industry
        # if industry == '':
        #     industry = contractDetails.stockType
        bw.set_industry(industry)

    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)

    def tickPrice(self, reqId, tickType, value, attrib):
        tickerId = str(reqId)
        bw = self.buyWrites[tickerId]
        tt = str(tickType)

        if reqId % 2 == 0:
            if tt == const.LASTPRICE:
                bw.tickData.ullst  = float(value)
            elif tt == const.BIDPRICE:
                bw.tickData.ulbid = float(value)
            elif tt == const.ASKPRICE:
                bw.tickData.ulask = float(value)
        else:
            if tt == const.LASTPRICE:
                bw.tickData.oplst  = float(value)
            elif tt == const.BIDPRICE:
                bw.tickData.opbid = float(value)
            elif tt == const.ASKPRICE:
                bw.tickData.opask = float(value)

    def updateAccountValue(self, key:str, val:str, currency:str, accountName:str):
        self.account.update(key,val)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)


    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)


    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)


    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)
