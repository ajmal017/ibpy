
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

        self.bw             = bw
        self.id             = bw["@id"]
        self.symbol         = bw["underlyer"]["@tickerSymbol"]
        self.tickerId       = ti
        self.industry       = ""
        self.ul_ts          = bw["@enteringTime"]
        self.rolled         = 0
        self.inibwprice      = float(bw["@enteringPrice"])
        self.position        = float(bw["@quantity"])

        self.strike         = float(bw["option"]["@strike"])
        self.expiry         = bw["option"]["@expiry"]
        self.earningscall         = bw["underlyer"]["@earningscall"]

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
                                    "when"            : rolling_item["@when"],
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
                                "when": bw["rolling_activities"]["rolled"]["@when"],
                                "from": bw["rolling_activities"]["rolled"]["@from"],
                                "to": bw["rolling_activities"]["rolled"]["@to"],
                                "strike": bw["rolling_activities"]["rolled"]["@strike"],
                                "buyprice": bw["rolling_activities"]["rolled"]["@buyprice"],
                                "sellprice": bw["rolling_activities"]["rolled"]["@sellprice"],
                                "ulprice": bw["rolling_activities"]["rolled"]["@ulprice"]
                            }
                        )

        self.realized = 0
        self.total = 0
        self.uncertaintyFlag = False
        self.oplastcalculated = False

        self.tickerData["ulbid"] = 0.0
        self.tickerData["ulask"] = 0.0
        self.tickerData["ullst"] = 0.0
        self.tickerData["opbid"] = 0.0
        self.tickerData["opask"] = 0.0
        self.tickerData["oplst"] = 0.0

        self.calc_rlzd()



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
            True,  #             globvars.header1['Id'         ] = "Unique Identifier"
            False, #             globvars.header1['Symbol'     ] = "Tickersymbol of underlyer"
            True,  #             globvars.header1['Industry'   ] = "Industry of Underlyer"
            True,  #             globvars.header1['Rolled'     ] = "How often this position was rolled"
            True,  #             globvars.header1['Pos'        ] = "How many legs"
            False, #             globvars.header1['Strike'     ] = "Strike"
            False, #             globvars.header1['Expiry'     ] = "Expiry"
            True, #             globvars.header1['Expiry'     ] = "Erngs.Call"
            True,  #             globvars.header1['Status'     ] = "In/Out/At the money at initiation and now ?"
            False, #             globvars.header1['UL-Init'    ] = "Price of underlyer when position was initiated"
            False, #             globvars.header1['OPT-Init'    ] = "Price of option when position was initiated"
            False, #             globvars.header1['BW-Price'   ] = "Initial buywrite price = UL-Price - Opt-premium"
            False, #             globvars.header1['BWP-Now'    ] = "Current price of this Buywrite"
            True,  #             globvars.header1['BWP-Prof'   ] = "Profit of the Buywrite"
            True,  #             globvars.header1['BWP-PL'     ] = ""
                   #
            False, #            globvars.header1['UL-Last'    ] = "underlyedr - last known price traded"
            True,  #          globvars.header1['ULL-BWP'    ] = "UL-Last minus bwprice (for detecting when breakeven will is reached)"
            False, #            globvars.header1['ULL-STRKE'  ] = "UL-Last - Strike"
            True,  #           globvars.header1['UL-Chge'    ] = "Change of UL-Price since initiation of position"
            True,  #          globvars.header1['UL-Chge pct'] = ".. in pct"
            True,  #          globvars.header1['UL-Bid'     ] = "last known bid for underlyer"
            True,  #          globvars.header1['UL-Ask'     ] = "last known ask for underlyer"
                   #
            False, #           globvars.header1['OP-Lst'     ] = "last known trade for underlyer"
            False, #           globvars.header1['OP-Bid'     ] = "last known bid for option"
            False, #           globvars.header1['OP-Ask'     ] = "last known ask for option"
                   #
            True,  #          globvars.header1['IIV'        ] = "initial intrinsic value for this option"
            True,  #          globvars.header1['IIV/$'      ] = "initial intrinsic value in dollar for this option"
            True,  #          globvars.header1['ITV'        ] = "initial Timevalue for this position"
            False, #          globvars.header1['ITV/$'      ] = "initial Timevalue in dollar for this position"
            True,  #         globvars.header1['CIV'        ] = "Current Intrinsic Value for this position"
            True,  #          globvars.header1['CIV/$'      ] = "Current Intrinsic Value in dollar for this position"
            True,  # globvars.header1['CTV'        ] = "Current TimeValue for this position"
            False, # globvars.header1['CTV/$'      ] = "Current TimeValue in dollar for this position"
            False, # globvars.header1['TV-Chg/%'   ] = "Change of Timevalue in %"
            False, # globvars.header1['TV-Prof'    ] = "Accumulated timevalue profit of this position"
            False, # globvars.header1['RLZD'       ] = "Realized from option buy back when rolling"
            False, # globvars.header1['UL-URPNL'   ] = "Unrealizerd PNL for Unterlyer"
            False, # globvars.header1['TOTAL'      ] = "Unrealizerd PNL for Unterlyer PLUS Realized from option buy back when rolling PLUS Accumulated timevalue profit of this position"
        ]

    def tvprof(self):
        if self.is_valid():
            return self.itv() * self.position * 100 - self.ctv()*self.position*100
        else:
            return 0

    def set_summary(self,data):
        self.total = data[37]

    def table_data(self):
        a = self.tickerData["opask"]
        b = self.tickerData["opbid"]

        if self.tickerData["oplst"] < 0.001:
            if a > 0.01 and b > 0.01:
                self.tickerData["oplst"] = (a + b) / 2
                if (a-b)/(a+b) < 0.3:
                    #Abweichung ask/bid nur 30%
                    self.oplastcalculated = True
                    self.uncertaintyFlag = False
                else:

                    #Abweichung sehr hoch: markieren
                    self.uncertaintyFlag = True
            else:
                #Abweichung sehr hoch: markieren
                self.uncertaintyFlag = True
        else:
            if self.oplastcalculated == True or self.tickerData["oplst"] < b or self.tickerData["oplst"] > a:
                self.tickerData["oplst"] = (a + b) / 2
                self.oplastcalculated = True

            self.uncertaintyFlag = False

        try:
            pcttvloss = self.ctv()/self.itv()
        except ZeroDivisionError:
            pcttvloss  = 0

        self.total = (float(self.tickerData["ullst"]) - float(self.bw["underlyer"]["@price"])) * self.position * 100 + \
                     self.realized + self.itv() * self.position * 100 - \
                     self.ctv() * self.position * 100 - \
                     self.civ() * self.position * 100 + \
                     self.iiv() * self.position * 100

        return (
            self.id,
            self.symbol,
            self.industry,
            self.rolled,
            self.position,
            "{:.2f}".format(self.strike),
            self.expiry,
            self.earningscall,
            self.get_ioa_initial() + "=>" + self.get_ioa_now(),
            "{:.2f}".format(self.inistkprice),          #UL-Init
            "{:.2f}".format(self.inioptprice),          #OPT-Init
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
            "{:.2f}".format(self.iiv()),
            "{:.2f}".format(self.iiv()*self.position*100),
            "{:.2f}".format(self.itv()),
            "{:.2f}".format(self.itv()*self.position*100),
            "{:.2f}".format(self.civ()),
            "{:.2f}".format(self.civ()*self.position*100),
            "{:.2f}".format(self.ctv()),
            "{:.2f}".format(self.ctv()*self.position*100),
            "{:.2f}".format(100*pcttvloss),
            "{:.2f}".format(self.itv() * self.position * 100 - self.ctv()*self.position*100),
            "{:.2f}".format(self.realized),
            "{:.2f}".format((float(self.tickerData["ullst"]) -  float(self.bw["underlyer"]["@price"])) * self.position * 100),
            "{:.2f}".format(self.total)
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
                self.inibwprice = self.inistkprice - self.inioptprice
                self.strike = float(ra["strike"])
                self.ul_ts  = ra["when"]
                self.expiry = ra["to"]
                self.rolled += 1


    def iiv(self):
        if self.inistkprice <= self.strike:
            # OTM
            ret = 0
        else:
            # ITM
            ret = float(self.inistkprice - self.strike)
        return ret

    def itv(self):
        if self.inistkprice <= self.strike:
            # OTM
            ret = self.inioptprice
        else:
            ret = self.inioptprice - self.iiv()
            # ITM
        return ret

    def ctv(self):
        if self.tickerData["ullst"] <= float(self.strike):
            #OTM
            return float(self.tickerData["oplst"])
        else:
            return float(self.tickerData["oplst"]) - self.civ()

    def civ(self):
        if self.tickerData["ullst"] <= float(self.strike):
            #OTM
            return float(0)
        else:
            return float(self.tickerData["ullst"]) - float(self.strike)

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





