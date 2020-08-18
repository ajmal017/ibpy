#from https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum

for i in range(91):
	print(TickTypeEnum.to_str(i), i)


import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

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
app.connect('127.0.0.1', 4002, 1)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
apple_contract = Contract()
apple_contract.symbol = 'AAPL'
apple_contract.secType = 'STK'
apple_contract.exchange = 'SMART'
apple_contract.currency = 'USD'

XAUUSD_contract = Contract()
XAUUSD_contract.symbol = 'XAUUSD'
XAUUSD_contract.secType = 'CMDTY'
XAUUSD_contract.exchange = 'SMART'
XAUUSD_contract.currency = 'USD'

BTC_futures__contract = Contract()
BTC_futures__contract.symbol = 'BRR'
BTC_futures__contract.secType = 'FUT'
BTC_futures__contract.exchange = 'CMECRYPTO'
BTC_futures__contract.lastTradeDateOrContractMonth  = '202003'

eurusd_contract = Contract()
eurusd_contract.symbol = 'EUR'
eurusd_contract.secType = 'CASH'
eurusd_contract.exchange = 'IDEALPRO'
eurusd_contract.currency = 'USD'

slv_opt_contract = Contract()
slv_opt_contract.symbol = "SLV   200821C00023500"
slv_opt_contract.secType = "OPT"
slv_opt_contract.exchange = "SMART"
slv_opt_contract.currency = "USD"


app.reqMktData(1, slv_opt_contract, '', False, False, [])

#Request Market Data
app.reqMktData(1, eurusd_contract, '', False, False, [])

time.sleep(10) #Sleep interval to allow time for incoming price data
app.disconnect()

