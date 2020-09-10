
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

    def __init__(self, bw: dict, ti: int):

        self.tickerData = {}

        self.symbol         = bw["underlyer"]["@tickerSymbol"]
        self.tickerId       = ti
        self.industry       = ""

        self.inibwprice      = float(bw["@enteringPrice"])
        self.position        = float(bw["@quantity"])

        self.strike         = float(bw["option"]["@strike"])
        self.expiry         = bw["option"]["@expiry"]

        self.inistkprice    = float(bw["underlyer"]["@price"])
        self.inioptprice    = float(bw["option"]["@price"])

        self.tickerData["oplst"]    = 0

        self.tickerData["ulbid"] = 0.0
        self.tickerData["ulask"] = 0.0
        self.tickerData["ullst"] = 0.0
        self.tickerData["opbid"] = 0.0
        self.tickerData["opask"] = 0.0
        self.tickerData["oplst"] = 0.0


    def is_valid(self):
        if self.tickerData["ullst"] > 1 and self.tickerData["oplst"] > 0.01:
            return True
        else:
            return False

    @staticmethod
    def header(self):
        return

    def table_data(self):
        return (
            self.symbol,
            self.industry,
            self.position,
            self.strike,
            self.expiry,
            self.get_ioa_initial(),
            self.inistkprice,
            self.inibwprice,
            self.tickerData["ullst"],
            self.tickerData["ullst"] - self.inistkprice,
            (self.tickerData["ullst"] - self.inistkprice)/self.inistkprice,
            self.tickerData["ulbid"],
            self.tickerData["ulask"],
            self.tickerData["oplst"],
            self.tickerData["opbid"],
            self.tickerData["opask"],
            self.itv(),
            self.itv()*self.position*100,
            self.ctv(),
            self.ctv()*self.position*100,
            100*self.ctv()/self.itv()
        )

    def ticker_id(self):
        return self.tickerId

    def get_ioa_initial(self):
        if (self.strike > self.inistkprice):
            ioa = "OTM"
        elif (self.strike < self.inistkprice):
            ioa = "ITM"
        else:
            ioa = "ATM"

    def get_ioa_now(self):
        if (self.strike > self.tickerData["ullst"]):
            ioa = "OTM"
        elif (self.strike < self.tickerData["ullst"]):
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
        return self.tickerData["ullst"]

    def set_stk_price(self,price):
        self.tickerData["ullst"] = price


    def set_opt_price(self,price):
        self.tickerData["oplst"] = price

    def itv(self):
        if self.inibwprice <= self.strike:
            # OTM
            ret = self.inioptprice
        else:
            # ITM
            ret = float(self.inioptprice - float(self.inistkprice - self.strike))
        return ret

    def ctv(self):
        if self.tickerData["ullst"] > float(self.strike):
            #ITM
            intrinsic_val = float(self.tickerData["ullst"]) - float(self.strike)
            return float(self.tickerData["oplst"]) - intrinsic_val
        else:
            return float(self.tickerData["oplst"])

    def underlyer(self):
        underlyer = Contract()
        underlyer.symbol = self.symbol
        underlyer.avPrice = self.inistkprice
        underlyer.secType = "STK"
        underlyer.exchange = "SMART"
        underlyer.currency = "USD"
        return underlyer

    def option(self):
        option = Contract()
        option.symbol = self.symbol
        option.avPrice = self.inioptprice
        option.secType = "OPT"
        option.exchange = "SMART"
        option.currency = "USD"
        option.lastTradeDateOrContractMonth = self.expiry
        option.strike = self.strike
        option.right = "Call"
        option.multiplier = "100"
        return option





