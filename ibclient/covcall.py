
from ibapi.contract import Contract
from datetime import datetime

class Security():
    def __init__(self):
        curbid = 0
        curask = 0
        curprice = 0
        avprice = 0

class covered_call():

    def __init__(self, right: str, underlyer: Contract, strike: float, expiry: datetime):
        self.ul = underlyer
        self.strike = strike
        self.right = right
        self.expiry = expiry
        self.stkprice = 0.0
        self.optprice = 0.0

    def set_stk_price(self,price):
        self.stkprice = price

    def set_opt_price(self,price):
        self.optprice = price

    def calc_itv(self,bw):
        if bw["underlyer"]["@price"] <= bw["option"]["@strike"]:
            # OTM
            itv = bw["option"]["@price"]
        else:
            # ITM
            itv = float(bw["option"]["@price"]) - float(float(bw["underlyer"]["@price"]) - float(bw["option"]["@strike"]))
        return float(itv)

    def getTimevalue(self):
        if self.stkprice > float(self.strike):
            #ITM
            intrinsic_val = float(self.stkprice) - float(self.strike)
            return float(self.optprice) - intrinsic_val
        else:
            return float(self.optprice)

    @staticmethod
    def get_contracts(bw):
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

        return (underlyer, option)





