from datetime import date, datetime

from ibapi.contract import Contract

class Security():
    def __init__(self):
        curbid = 0
        curask = 0
        curprice = 0
        avprice = 0

class TickData():
    def __init__(self, ti):
        self.tickerId = ti
        self.ulbid = 0.0
        self.ulask = 0.0
        self.ullst = 0.0
        self.opbid = 0.0
        self.opask = 0.0
        self.oplst = 0.0

class CalcData():
    def __init__(self):
        self.timeValue = ""

class StatData():
    def __init__(self, bw):
        self.rollingActivity = []
        self.buyWrite = bw
        self.industry = ""
        self.inibwprice      = float(bw["@enteringPrice"])
        self.enteringTime    = bw["@enteringTime"]
        self.position        = float(bw["@quantity"])
        self.strike          = float(bw["option"]["@strike"])
        self.inistkprice     = float(bw["underlyer"]["@price"])
        self.inioptprice     = float(bw["option"]["@price"])
        self.expiry          = bw["option"]["@expiry"]
        self.earningscall    = bw["underlyer"]["@earningscall"]

        if "rolling_activities" in bw:
            if bw["rolling_activities"] != None:
                if len(bw["rolling_activities"]) > 0:
                    #wegen Unschoenheit oder Bug in xmltodict:
                    if type(bw["rolling_activities"]["rolled"]) == list:
                        for rolling_item in bw["rolling_activities"]["rolled"]:
                            self.rollingActivity.append(
                                {
                                    "when"          : rolling_item["@when"],
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
                                "when":         bw["rolling_activities"]["rolled"]["@when"],
                                "from":         bw["rolling_activities"]["rolled"]["@from"],
                                "to":           bw["rolling_activities"]["rolled"]["@to"],
                                "strike":       bw["rolling_activities"]["rolled"]["@strike"],
                                "buyprice":     bw["rolling_activities"]["rolled"]["@buyprice"],
                                "sellprice":    bw["rolling_activities"]["rolled"]["@sellprice"],
                                "ulprice":      bw["rolling_activities"]["rolled"]["@ulprice"]
                            }
                        )

    def get_ioa_initial(self):
        if (self.strike > self.inistkprice):
            ioa = "O"
        elif (self.strike < self.inistkprice):
            ioa = "I"
        else:
            ioa = "A"
        return ioa

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


class covered_call():

    def __init__(self, bw: dict, ti: int):

        self.statData = StatData(bw)    # static (from configfile)
        self.tickData = TickData(ti)          # dynamic (from Brokerconnection)
        self.calcData = CalcData()          #¨calculated (derivated from the other two)

        self.realized = 0
        self.total = 0
        self.uncertaintyFlag = False
        self.oplastcalculated = False
        self.calc_rlzd()

        self.dispData = self.table_data()

    def is_valid(self):
        if self.tickData.ullst > 1 and self.tickData.oplst > 0.01 and self.statData.itv() > 0:
            return True
        else:
            return False

    def updateData(self):
        self.dispData = self.table_data()
        pass

    @staticmethod
    def columns_hidden():
        return [
            False,  #             globvars.header1['Id'         ] = "Unique Identifier"
            False, #             globvars.header1['Symbol'     ] = "Tickersymbol of underlyer"
            True,  #             globvars.header1['Industry'   ] = "Industry of Underlyer"
            False,  #             globvars.header1['Rolled'     ] = "How often this position was rolled"
            True,  #             globvars.header1['Pos'        ] = "How many legs"
            False, #             globvars.header1['Strike'     ] = "Duration"
            False, #             globvars.header1['Strike'     ] = "Strike"
            False, #             globvars.header1['Expiry'     ] = "Expiry"
            False, #             globvars.header1['Expiry'     ] = "Erngs.Call"
            True,  #             globvars.header1['Status'     ] = "In/Out/At the money at initiation and now ?"
            False, #             globvars.header1['UL-Init'    ] = "Price of underlyer when position was initiated"
            False, #             globvars.header1['OPT-Init'    ] = "Price of option when position was initiated"
            False, #             globvars.header1['BW-Price'   ] = "Initial buywrite price = UL-Price - Opt-premium"
            False, #             globvars.header1['BWP-Now'    ] = "Current price of this Buywrite"
            False,  #             globvars.header1['BWP-Prof'   ] = "Profit of the Buywrite"
            True,  #             globvars.header1['BWP-PL'     ] = ""
                   #
            False, #            globvars.header1['UL-Last'    ] = "underlyedr - last known price traded"
            False,  #          globvars.header1['ULL-BWP'    ] = "UL-Last minus bwprice (for detecting when breakeven will is reached)"
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
            False,  #          globvars.header1['IIV/$'      ] = "initial intrinsic value in dollar for this option"
            True,  #          globvars.header1['ITV'        ] = "initial Timevalue for this position"
            False, #          globvars.header1['ITV/$'      ] = "initial Timevalue in dollar for this position"
            True,  #         globvars.header1['CIV'        ] = "Current Intrinsic Value for this position"
            False,  #          globvars.header1['CIV/$'      ] = "Current Intrinsic Value in dollar for this position"
            True,  # globvars.header1['CTV'        ] = "Current TimeValue for this position"
            False, # globvars.header1['CTV/$'      ] = "Current TimeValue in dollar for this position"
            False, # globvars.header1['TV-Chg/%'   ] = "Change of Timevalue in %"
            False, # globvars.header1['TV-Prof'    ] = "Accumulated timevalue profit of this position"
            False, # globvars.header1['RLZD'       ] = "Realized from option buy back when rolling"
            False, # globvars.header1['UL-URPNL'   ] = "Unrealizerd PNL for Unterlyer"
            False, # globvars.header1['TOTAL'      ] = "Unrealizerd PNL for Unterlyer PLUS Realized from option buy back when rolling PLUS Accumulated timevalue profit of this position"
        ]

    def get_ioa_now(self):
        if (self.statData.strike > self.tickData.ullst):
            ioa = "O"
        elif (self.statData.strike < self.tickData.ullst):
            ioa = "I"
        else:
            ioa = "A"
        return ioa

    def tvprof(self):
        if self.is_valid():
            return self.statData.itv() * self.statData.position * 100 - self.ctv()*self.statData.position*100
        else:
            return 0

    def set_summary(self,data):
        self.total = data[37]

    def table_data(self):

        self.total = 0
        ulurpnl = 0
        ullstrikemargin = 0
        pcttvloss = 0

        a = self.tickData.opask
        b = self.tickData.opbid

        if self.tickData.oplst < 0.001:
            if a > 0.01 and b > 0.01:
                self.tickData.oplst = (a + b) / 2
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
            if self.oplastcalculated == True or self.tickData.oplst < b or self.tickData.oplst > a:
                if a > 0.01 and b > 0.01:
                    self.tickData.oplst = (a + b) / 2
                    self.oplastcalculated = True

            self.uncertaintyFlag = False


        try:
            pcttvloss = self.ctv()/self.statData.itv()
        except ZeroDivisionError:
            pcttvloss  = 0

        try:
            ullstrikemargin = (self.tickData.ullst - self.statData.strike) / self.tickData.ullst
        except ZeroDivisionError:
            ullstrikemargin  = 0


        if float(self.tickData.ullst) > 0.1:
            self.total = (float(self.tickData.ullst) - float(self.statData.buyWrite["underlyer"]["@price"])) * self.statData.position * 100 + \
                         self.realized + self.statData.itv() * self.statData.position * 100 - \
                         self.ctv() * self.statData.position * 100 - \
                         self.civ() * self.statData.position * 100 + \
                         self.statData.iiv() * self.statData.position * 100
            ulurpnl = (float(self.tickData.ullst) - float(self.statData.buyWrite["underlyer"]["@price"])) * self.statData.position * 100
        else:
            self.total = 0
            ulurpnl = 0

        beg1 = self.statData.buyWrite["@enteringTime"]
        try:
            beg = datetime.strptime(beg1, "%Y %b %d %H:%M:%S")
            timePassed = datetime.now()-beg
            self.statData.duration = str(timePassed.days)
        except:
            self.statData.duration = "0 D"

        self.downSideProtPct = self.calcDownSideProtection()
        self.upSidePotentPct = self.calcUpSidePotential()

        return (
            "{:.2f}".format(100 * pcttvloss),
            self.statData.buyWrite["underlyer"]["@tickerSymbol"],
            self.statData.industry,
            len(self.statData.rollingActivity),
            self.statData.position,
            self.statData.duration,
            "{:.2f}".format(self.statData.strike),
            datetime.strptime(self.statData.expiry, "%Y%m%d").strftime("%d.%m"),
            self.statData.earningscall,
            self.statData.get_ioa_initial() + "=>" + self.get_ioa_now(),
            "{:.2f}".format(self.statData.inistkprice),          #UL-Init
            "{:.2f}".format(self.statData.inioptprice),          #OPT-Init
            "{:.2f}".format(self.statData.inibwprice),           #BW-Price
            "{:.2f}".format(self.tickData.ullst - self.tickData.oplst),   #actual value of buywrite (last ul price - last option price
            "{:.2f}".format(self.tickData.ullst - self.tickData.oplst - self.statData.inibwprice),  # Profit or Loss of Buywrite
            "{:.2f}".format((self.tickData.ullst - self.tickData.oplst - self.statData.inibwprice)*self.statData.position*100), #current Profit or Loss in USD
            "{:.2f}".format(self.tickData.ullst),
            "{:.2f}".format(self.tickData.ullst - self.statData.inibwprice),
            "{:.2f}".format(ullstrikemargin),
            "{:.2f}".format(self.tickData.ullst - self.statData.inistkprice),
            "{:.2f}".format((self.tickData.ullst - self.statData.inistkprice)/self.statData.inistkprice),
            "{:.2f}".format(self.tickData.ulbid),
            "{:.2f}".format(self.tickData.ulask),
            "{:.2f}".format(self.tickData.oplst),
            "{:.2f}".format(self.tickData.opbid),
            "{:.2f}".format(self.tickData.opask),
            "{:.2f}".format(self.statData.iiv()),
            "{:.2f}".format(self.statData.iiv()*self.statData.position*100),
            "{:.2f}".format(self.statData.itv()),
            "{:.2f}".format(self.statData.itv()*self.statData.position*100),
            "{:.2f}".format(self.civ()),
            "{:.2f}".format(self.civ()*self.statData.position*100),
            "{:.2f}".format(self.ctv()),
            "{:.2f}".format(self.ctv()*self.statData.position*100),
            "{:.2f}".format(self.downSideProtPct),
            "{:.2f}".format(self.upSidePotentPct),
            self.statData.buyWrite["@id"],
            "{:.2f}".format(self.statData.itv() * self.statData.position * 100 - self.ctv()*self.statData.position*100),
            "{:.2f}".format(self.realized),
            "{:.2f}".format(ulurpnl),
            "{:.2f}".format(self.total)
        )

    def ticker_id(self):
        return self.statData.tickerId

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
        self.statData.industry = i

    def get_industry(self):
        return self.statData.industry

    def get_expiry(self):
        return (self.statData.expiry)

    def get_strike(self):
        return (self.statData.strike)

    def get_stk_price(self):
        return self.tickData.ullst

    def set_stk_price(self,price):
        self.tickData.ullst = price

    def set_opt_price(self,price):
        self.tickData.oplst = price

    def calc_rlzd(self):
        if len(self.statData.rollingActivity) > 0:
            for ra in self.statData.rollingActivity:

                self.realized = self.realized + 100 * self.statData.position * (self.statData.inioptprice - float(ra["buyprice"]))
                self.statData.inioptprice = float(ra["sellprice"])
                self.statData.inistkprice = float(ra["ulprice"])
                self.inibwprice = self.statData.inistkprice - self.statData.inioptprice
                self.statData.strike = float(ra["strike"])
                self.ul_ts  = ra["when"]
                self.statData.expiry = ra["to"]

    def ctv(self):
        if self.tickData.ullst <= float(self.statData.strike):
            #OTM
            return float(self.tickData.oplst)
        else:
            return float(self.tickData.oplst) - self.civ()

    def civ(self):
        if self.tickData.ullst <= float(self.statData.strike):
            #OTM
            return float(0)
        else:
            return float(self.tickData.ullst) - float(self.statData.strike)

    def calcDownSideProtection(self):
        if self.tickData.ullst == 0 or self.tickData.ullst <= float(self.statData.strike):
            #OTM
            return float(0)
        else:
            return 100*((self.tickData.ullst - float(self.statData.strike)) / self.tickData.ullst)

    def calcUpSidePotential(self):
        if self.tickData.ullst == 0 or self.tickData.ullst > float(self.statData.strike):
            #OTM
            return float(0)
        else:
            return 100*((float(self.statData.strike) - self.tickData.ullst ) / self.tickData.ullst)

    def underlyer(self):
        underlyer = Contract()
        underlyer.symbol = self.statData.buyWrite["underlyer"]["@tickerSymbol"]
        underlyer.avPrice = self.statData.inistkprice
        underlyer.secType = "STK"
        underlyer.exchange = "SMART"
        underlyer.currency = "USD"
        return underlyer

    def option(self):
        option = Contract()
        option.symbol = self.statData.buyWrite["underlyer"]["@tickerSymbol"]
        option.avPrice = self.statData.inioptprice
        option.secType = "OPT"
        option.exchange = "SMART"
        option.currency = "USD"
        option.lastTradeDateOrContractMonth = self.statData.expiry
        option.strike = self.statData.strike
        option.right = "Call"
        option.multiplier = "100"

        return option





