#from https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum
import logger as logger
from globals import globvars

import datetime
from covcall import covered_call

import threading
import time

import xmltodict

with open('cc.xml') as fd:
    ccdict = xmltodict.parse(fd.read())

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

date_time_str = '2020-09-18 22:00:00.000000'
date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

date_time_str = '2020-09-18 22:00:00.000000'
date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

def run_loop():
    app.run()

globvars.init_globvars()

app = IBapi()
app.connect('127.0.0.1', 4002, 3)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

mainLogger = logger.initMainLogger()
mainLogger.info('Started')

initialTickerId = 4100


tv=[]
itv=[]


tickerId = initialTickerId
for bw in ccdict["coveredCalls"]["bw"]:
    bw["tickerId"] = tickerId

    underlyer = Contract()
    underlyer.symbol = bw["underlyer"]["@tickerSymbol"]
    underlyer.secType = "STK"
    underlyer.exchange = "SMART"
    underlyer.currency = "USD"

    option = Contract()
    option.symbol = bw["underlyer"]["@tickerSymbol"]
    option.secType = "OPT"
    option.exchange = "SMART"
    option.currency = "USD"
    option.lastTradeDateOrContractMonth = bw["option"]["@expiry"]
    option.strike = bw["option"]["@strike"]
    option.right = "Call"
    option.multiplier = "100"

    now = datetime.datetime.now()
    dt = now.strftime("%Y%m%d %H:%M:00")
    app.reqHistoricalData(bw["tickerId"], option, dt, "30 S", "5 secs", "MIDPOINT", 1, 1, False, [])
    app.reqHistoricalData(bw["tickerId"]+1, underlyer, dt, "30 S", "5 secs", "MIDPOINT", 1, 1, False, [])
    tv.append(0)
    itv.append(0)
    tickerId += 2

time.sleep(10) #Sleep interval to allow time for connection to server

allfinished = False
while allfinished == False:
    allfinished = True

    for bw in ccdict["coveredCalls"]["bw"]:
        while bw["tickerId"] not in endflag:
            time.sleep(1)
        if endflag[bw["tickerId"]] == False:

            allfinished = False

close_price = lambda x,ti: x[ti][-1]
pr = {}



#initial timevalues:
for bwnum,bw in enumerate(ccdict["coveredCalls"]["bw"]):
    underlyer = Contract()
    underlyer.symbol = bw["underlyer"]["@tickerSymbol"]
    underlyer.secType = "STK"
    underlyer.exchange = "SMART"
    underlyer.currency = "USD"
    cc = covered_call(underlyer, "C", float(bw["option"]["@strike"]), date_time_obj)
    cc.set_stk_price(float(bw["underlyer"]["@price"]))
    cc.set_opt_price(float(bw["option"]["@price"]))
    itv[bwnum] = cc.getTimevalue()
    #mainLogger.info('initial timevalue of %s is %f',underlyer.symbol,itv[bwnum])

tickerId = initialTickerId
for bwnum,bw in enumerate(ccdict["coveredCalls"]["bw"]):
    pr["option"]  = close_price(bars, tickerId)
    pr["stock"] = close_price(bars, tickerId+1)

    underlyer = Contract()
    underlyer.symbol = bw["underlyer"]["@tickerSymbol"]
    underlyer.secType = "STK"
    underlyer.exchange = "SMART"

    cc = covered_call(underlyer, "C", float(bw["option"]["@strike"]), date_time_obj)

    cc.set_stk_price(pr["stock"].close)
    cc.set_opt_price(pr["option"].close)
    tv[bwnum] = cc.getTimevalue()
    #mainLogger.info ("timevalue of %s is %f",underlyer.symbol,tv[bwnum])
    tickerId +=2

for bwnum,bw in enumerate(ccdict["coveredCalls"]["bw"]):
    mainLogger.info ("timevalue of %s is down to %f pct (from %f to %f)",bw["underlyer"]["@tickerSymbol"],100*tv[bwnum]/itv[bwnum], itv[bwnum], tv[bwnum])

app.disconnect()

