
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
        self.rollingActivity = []

        self.id             = bw["@id"]
        self.symbol         = bw["underlyer"]["@tickerSymbol"]
        self.tickerId       = ti
        self.industry       = ""

        self.inibwprice      = float(bw["@enteringPrice"])
        self.position        = float(bw["@quantity"])

        self.strike         = float(bw["option"]["@strike"])
        self.expiry         = bw["option"]["@expiry"]

        self.inistkprice    = float(bw["underlyer"]["@price"])
        self.inioptprice    = float(bw["option"]["@price"])

        if "rolling_activities" in bw:
            if bw["rolling_activities"] != None:
                if len(bw["rolling_activities"]) > 0:
                    #wegen Unschoenheit oder Bug in xmltodict:
                    if type(bw["rolling_activities"]["rolled"]) == list:
                        for rolling_item in bw["rolling_activities"]["rolled"]:
                            self.rollingActivity.append(
                                {
                                    "from"          : rolling_item["@from"],
                                    "to"            : rolling_item["@to"],
                                    "strike"        : rolling_item["@strike"],
                                    "buyprice"      : rolling_item["@buyprice"],
                                    "sellprice"     : rolling_item["@sellprice"],
                                    "ulprice"       : rolling_item["@ulprice"]
                                }
                            )
                    else:
                        self.rollingActivity.append(
                            {
                                "from": bw["rolling_activities"]["rolled"]["@from"],
                                "to": bw["rolling_activities"]["rolled"]["@to"],
                                "strike": bw["rolling_activities"]["rolled"]["@strike"],
                                "buyprice": bw["rolling_activities"]["rolled"]["@buyprice"],
                                "sellprice": bw["rolling_activities"]["rolled"]["@sellprice"],
                                "ulprice": bw["rolling_activities"]["rolled"]["@ulprice"]
                            }
                        )

        self.realized = 0
        self.calc_rlzd()

        self.oplastcalculated = False

        self.tickerData["ulbid"] = 0.0
        self.tickerData["ulask"] = 0.0
        self.tickerData["ullst"] = 0.0
        self.tickerData["opbid"] = 0.0
        self.tickerData["opask"] = 0.0
        self.tickerData["oplst"] = 0.0


    def is_valid(self):
        if "ullst" in self.tickerData and "oplst" in self.tickerData:
            if self.tickerData["ullst"] > 1 and self.tickerData["oplst"] > 0.01 and self.itv() > 0:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def columns_hidden():
        return [
            False, #0
            False, #1
            False, #2
            False, #3
            False, #4
            False, #5
            False, #6
            False, #7
            False, #8
            False, #9
            False, #10
            False, #11
            False, #12
            True,  #13
            True,  #14
            False, #15
            True,  #16
            True,  #17
            False, #18
            False, #19
            False, #20
            False, #21
            False, #22
            False,  #23
            False  # 23
        ]

    def tvprof(self):
        if self.is_valid():
            return self.itv() * self.position * 100 - self.ctv()*self.position*100
        else:
            return 0

    def table_data(self):
        if self.tickerData["oplst"] < 0.001:
            a = self.tickerData["opask"]
            b = self.tickerData["opbid"]
            if a > 0.01 and b > 0.01:
                if (a-b)/(a+b) < 0.3:
                    self.tickerData["oplst"] = (a+b)/2
                    self.oplastcalculated = True

        return (
            self.id,
            self.symbol,
            self.industry,
            self.position,
            "{:.2f}".format(self.strike),
            self.expiry,
            self.get_ioa_initial() + "=>" + self.get_ioa_now(),
            "{:.2f}".format(self.inistkprice),          #UL-Init
            "{:.2f}".format(self.inibwprice),           #BW-Price
            "{:.2f}".format(self.tickerData["ullst"] - self.tickerData["oplst"]),   #actual value of buywrite (last ul price - last option price
            "{:.2f}".format(self.tickerData["ullst"] - self.tickerData["oplst"] - self.inibwprice), # Profit or Loss of Buywrite
            "{:.2f}".format((self.tickerData["ullst"] - self.tickerData["oplst"] - self.inibwprice)*self.position*100), #current Profit or Loss in USD
            "{:.2f}".format(self.tickerData["ullst"]),
            "{:.2f}".format(self.tickerData["ullst"] - self.inibwprice),
            "{:.2f}".format(self.tickerData["ullst"] - self.strike),
            "{:.2f}".format(self.tickerData["ullst"] - self.inistkprice),
            "{:.2f}".format((self.tickerData["ullst"] - self.inistkprice)/self.inistkprice),
            "{:.2f}".format(self.tickerData["ulbid"]),
            "{:.2f}".format(self.tickerData["ulask"]),
            "{:.2f}".format(self.tickerData["oplst"]),
            "{:.2f}".format(self.tickerData["opbid"]),
            "{:.2f}".format(self.tickerData["opask"]),
            "{:.2f}".format(self.itv()),
            "{:.2f}".format(self.itv()*self.position*100),
            "{:.2f}".format(self.ctv()),
            "{:.2f}".format(self.ctv()*self.position*100),
            "{:.2f}".format(100*self.ctv()/self.itv()),
            "{:.2f}".format(self.itv() * self.position * 100 - self.ctv()*self.position*100),
            "{:.2f}".format(self.realized)
        )

    def ticker_id(self):
        return self.tickerId

    def get_ioa_initial(self):
        if (self.strike > self.inistkprice):
            ioa = "O"
        elif (self.strike < self.inistkprice):
            ioa = "I"
        else:
            ioa = "A"
        return ioa

    def get_ioa_now(self):
        if (self.strike > self.tickerData["ullst"]):
            ioa = "O"
        elif (self.strike < self.tickerData["ullst"]):
            ioa = "I"
        else:
            ioa = "A"
        return ioa

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

    def calc_rlzd(self):
        if len(self.rollingActivity) > 0:
            for ra in self.rollingActivity:
                self.realized = self.realized + 100 * self.position * (self.inioptprice - float(ra["buyprice"]))
                self.inioptprice = float(ra["sellprice"])
                self.inistkprice = float(ra["ulprice"])
                self.strike = float(ra["strike"])
                self.expiry = ra["to"]


    def itv(self):
        if self.inistkprice <= self.strike:
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





