
from ibapi.contract import Contract
from datetime import datetime
from datetime import date

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
        self.industry = ""

    def get_ioa_initial(self):
        if (self.strike > self.stkprice):
            ioa = "OTM"
        elif (self.strike < self.stkprice):
            ioa = "ITM"
        else:
            ioa = "ATM"

    def get_ioa_now(self):
        if (self.strike > self.stkprice):
            ioa = "OTM"
        elif (self.strike < self.stkprice):
            ioa = "ITM"
        else:
            ioa = "ATM"

    def get_days(self):
        ys = self.expiry[0:4]
        ms = self.expiry[4:6]
        ds = self.expiry[6:8]
        year = int(ys)
        month = int(ms)
        day = int(ds)

        d1 = date(year, month, day)
        d0 = date.today()
        delta = d1 - d0
        return delta.days

    def set_industry(self, i):
        self.industry = i

    def get_industry(self):
        return self.industry

    def get_expiry(self):
        return (self.expiry)

    def get_strike(self):
        return (self.strike)

    def get_stk_price(self):
        return self.stkprice

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
        underlyer.avPrice = bw["underlyer"]["@price"]
        underlyer.secType = "STK"
        underlyer.exchange = "SMART"
        underlyer.currency = "USD"

        option = Contract()
        option.symbol = bw["underlyer"]["@tickerSymbol"]
        option.avPrice = bw["option"]["@price"]
        option.secType = "OPT"
        option.exchange = "SMART"
        option.currency = "USD"
        option.lastTradeDateOrContractMonth = bw["option"]["@expiry"]
        option.strike = bw["option"]["@strike"]
        option.right = "Call"
        option.multiplier = "100"

        return (underlyer, option)





