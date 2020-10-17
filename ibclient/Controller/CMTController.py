import os
import re
import datetime

import Misc.const
import Model
from Misc.globals import globvars
from Model.download_bars import DownloadApp

class Controller:
    def __init__(self, model):
        self.model = model
        self.autoUpdate = True

    def initData(self,v):
        self.view = v

    def getStockData(self, cc):
        return self.model.getHistStockData(cc)

    def updateHistory(self, do_overwrite=False, forced_startdate = "20200501", forced_enddate = "20201017"):
        datetimepattern=""
        latest = {}
        newest = {}
        contracts=[]
        optpat = re.compile(Misc.const.DATADIR + r"\\(...)_(.+)\\1_min\\(\w*)(....)(..)(..)C(.+)$")
        stkpat = re.compile(Misc.const.DATADIR + r"\\(...)_(.+)\\1_min\\(\w*)$")
        barwidth = "1_min"
        for root, dirs, files in os.walk(Misc.const.DATADIR):
            o = optpat.match(root)
            if o:
                (dt, type, ul, expiry_y, expiry_m, expiry_d, strike) = o.groups(0)
                if ul == "DEMO" or ul == "CTLT":
                    continue

                expiry_d = expiry_y + expiry_m + expiry_d

                ctrct = self.model.brkConnection.make_contract(ul, dt, "USD", "SMART", expiry_d, strike)
                contracts.append(ctrct)
                newest[ctrct] = {}
                newest[ctrct]["c"] = datetime.datetime.strptime("20200701", "%Y%m%d")
                newest[ctrct]["t"] = type
                nextname = datetime.datetime.strftime(newest[ctrct]["c"] + datetime.timedelta(1),
                                                      "%Y%m%d") + ".csv"
                newest[ctrct]["f"] = os.path.join(root, nextname)

                for name in files:
                    #option

                    if type != "MIDPOINT":
                        continue

                    if dt not in latest:
                        latest[dt]={}
                    if type not in latest[dt]:
                        latest[dt][type] = {}
                    if barwidth not in latest[dt][type]:
                        latest[dt][type][barwidth] = {}
                    if ul not in latest[dt][type][barwidth]:
                        latest[dt][type][barwidth][ul] = {}
                    if expiry_d not in latest[dt][type][barwidth][ul]:
                        latest[dt][type][barwidth][ul][expiry_d] = {}
                    if strike not in latest[dt][type][barwidth][ul][expiry_d]:
                        latest[dt][type][barwidth][ul][expiry_d][strike] = {}

                    m = re.match(r"^(....)(..)(..)\.csv", name)
                    if m:
                        y, m, d = m.groups(0)

                        if newest[ctrct]["c"] < datetime.datetime.strptime(y + m + d, "%Y%m%d"):
                            newest[ctrct]["c"] = datetime.datetime.strptime(y + m + d, "%Y%m%d")
                            nextname = datetime.datetime.strftime(newest[ctrct]["c"] + datetime.timedelta(1),
                                                                  "%Y%m%d") + ".csv"
                            newest[ctrct]["f"] = os.path.join(root, nextname)
            else:
                s = stkpat.match(root)
                if s:
                    (dt, type, ul) = s.groups(0)
                    if ul == "DEMO" or ul == "CTLT":
                        continue
                    ctrct = self.model.brkConnection.make_contract(ul, dt, "USD", "SMART")
                    contracts.append(ctrct)
                    newest[ctrct] = {}
                    newest[ctrct]["c"] = datetime.datetime.strptime("20200501", "%Y%m%d")
                    newest[ctrct]["t"] = type
                    nextname = datetime.datetime.strftime(newest[ctrct]["c"] + datetime.timedelta(1), "%Y%m%d") + ".csv"

                    newest[ctrct]["f"] = os.path.join(root, nextname)

                    for name in files:
                        if dt not in latest:
                            latest[dt]={}
                        if type not in latest[dt]:
                            latest[dt][type] = {}
                        if barwidth not in latest[dt][type]:
                            latest[dt][type][barwidth] = {}
                        if ul not in latest[dt][type][barwidth]:
                            latest[dt][type][barwidth][ul] = {}

                        m = re.match(r"^(....)(..)(..)\.csv", name)
                        if m:
                            y,m,d = m.groups(0)

                            if newest[ctrct]["c"] < datetime.datetime.strptime(y + m + d,"%Y%m%d"):
                                    newest[ctrct]["c"] = datetime.datetime.strptime(y+m+d, "%Y%m%d")
                                    nextname = datetime.datetime.strftime(newest[ctrct]["c"]+datetime.timedelta(1), "%Y%m%d")+".csv"
                                    newest[ctrct]["f"] = os.path.join(root,nextname)

        with open("downHist.ps1","w") as f:
            for ctrct in newest:
                newestdate=newest[ctrct]["c"].date()
                today = datetime.datetime.today().date()
                csvfile = newest[ctrct]["f"]
                if  today > newestdate+datetime.timedelta(1) or do_overwrite == True:
                    if not os.path.exists(csvfile) or do_overwrite == True:
                        # Posiible datatypes: TRADES, MIDPOINT, BID, ASK, BID_ASK, ADJUSTED_LAST, HISTORICAL_VOLATILITY, OPTION_IMPLIED_VOLATILITY, REBATE_RATE, FEE_RATE, YIELD_BID, YIELD_ASK, YIELD_BID_ASK, YIELD_LAST
                        if do_overwrite == True:
                            startdate = forced_startdate
                            enddate = forced_enddate
                            datatypes = ["TRADES", "BID", "ASK", "BID_ASK", "ADJUSTED_LAST",
                                         "HISTORICAL_VOLATILITY", "OPTION_IMPLIED_VOLATILITY"]
                        else:
                            startdate = datetime.datetime.strftime(newestdate, "%Y%m%d")
                            enddate = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
                            datatypes = [newest[ctrct]["t"]]

                        if startdate != enddate:
                            if ctrct.secType == "OPT":
                                for dt in datatypes:
                                    f.write('py .\download.py --port "4002" --security-type "OPT" --size "1 min" '+
                                          ' --start-date '+ startdate +
                                          ' --end-date '+ enddate +
                                          ' --data-type ' +  dt +
                                          ' --expiry '+ ctrct.lastTradeDateOrContractMonth +
                                          ' --strike ' + ctrct.strike +
                                          '  ' + ctrct.symbol+"\n")
                            else:

                                for dt in datatypes:
                                    f.write('py .\download.py --port "4002" --security-type "STK" --size "1 min" ' +
                                          ' --start-date '+ startdate +
                                          ' --end-date '+ enddate +
                                          ' --data-type ' +  dt +
                                          '  ' + ctrct.symbol+"\n")
        return



    def getNumPositions(self):
        return self.model.getNumPositions()

    def connect(self):
        self.model.connectBroker()

    def disconnect(self):
        self.model.disconnectBroker()

    def changeBrokerPort(self, port):
        self.model.changeBrokerPort(port)

    def toggleAutoUpdate(self):
        if self.autoUpdate == True:
            self.autoUpdate = False
        else:
            self.autoUpdate = True

        self.model.setAutoUpdate(self.autoUpdate)

    def resetAllColumns(self):
        self.view.resetAllColumns()

    def showAllColumns(self):
        l = self.model.columnCount(None)
        self.view.showAllColumns(l)

    def clearSelection(self):
        self.view.clearSelection()
