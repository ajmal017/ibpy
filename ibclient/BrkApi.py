from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum

from globals import globvars
import const

class BrkApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.bars={}
        self.endflag = {}

    def historicalData(self, reqId, bar):

        tickerId = str(reqId)
        bw = globvars.tickerData[tickerId]["bw"]

        if reqId not in self.bars:
            self.bars[reqId] = []

        # print(reqId, "BarData.", bar)

        if reqId % 2 == 0:
            bw["cc"].set_stk_price(bar.close)
        else:
            bw["cc"].set_opt_price(bar.close)

        globvars.tickerData[tickerId][const.LASTPRICE] = bar.close

        self.bars[reqId].append(bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        if reqId not in self.endflag:
            self.endflag[reqId] = False
        super().historicalDataEnd(reqId, start, end)
        # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.endflag[reqId] = True

    def historicalDataUpdate(self, reqId: int, bar):
         print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)


    def tickPrice(self, reqId, tickType, value, attrib):
        tickerId = str(reqId)

        bw = globvars.tickerData[tickerId]["bw"]

        if str(tickType) == const.LASTPRICE :
            if reqId % 2 == 0:
                bw["cc"].set_stk_price(value)
            else:
                bw["cc"].set_opt_price(value)
            globvars.tickerData[tickerId][const.LASTPRICE] = value
            #print('The currenttv of ', tickerData[tickerId]["bw"]["underlyer"]["@tickerSymbol"], " is ",bw["cc"].getTimevalue())


        if str(tickType) == const.ASKPRICE :
            globvars.tickerData[tickerId][const.ASKPRICE] = value

        if str(tickType) == const.BIDPRICE :
            globvars.tickerData[tickerId][const.BIDPRICE] = value

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
