#from https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum

import datetime

import threading
import time
bars = {}
endflag = {}

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def historicalData(self, reqId, bar):
        if reqId not in bars:
            bars[reqId] = []
        print(reqId, "BarData.", bar)
        bars[reqId].append(bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        if reqId not in endflag:
            endflag[reqId] = False
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        endflag[reqId] = True

    def historicalDataUpdate(self, reqId: int, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)


    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2 and reqId == 1:
            print('The current ask price is: ', price)


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


def run_loop():
    app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 2)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server


def underlyer():
    contract = Contract()
    contract.symbol = "IBKR"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    return contract

def option():
    contract = Contract()
    contract.symbol = "IBKR"
    contract.secType = "OPT"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.lastTradeDateOrContractMonth = "20200918"
    contract.strike = "50"
    contract.right = "Call"
    contract.multiplier = "100"
    return contract

tickerIds = [4102,4103]

i=0
app.reqHistoricalData(tickerIds[i], option(), "20200823 10:50:25", "1 D", "1 hour", "MIDPOINT", 1, 1, False, [])
i = i + 1
app.reqHistoricalData(tickerIds[i], stock(), "20200823 10:50:25", "1 D", "1 hour", "MIDPOINT", 1, 1, False, [])


time.sleep(1) #Sleep interval to allow time for incoming price data

allfinished = False
while allfinished == False:
    allfinished = True
    for i in tickerIds:
        if endflag[i] == False:
            allfinished = False

#time.sleep(10) #Sleep interval to allow time for incoming price data

x = bars

app.disconnect()

