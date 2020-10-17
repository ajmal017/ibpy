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
        self.model.getHistStockData(cc)
        pass

    def updateHistory(self):
        datetimepattern=""
        latest = {}
        newest = {}
        contracts=[]
        optpat = re.compile(Misc.const.DATADIR + r"\\(...)_(.+)\\(.....)\\(\w*)(....)(..)(..)C(.+)$")
        stkpat = re.compile(Misc.const.DATADIR + r"\\(...)_(.+)\\(.....)\\(\w*)$")

        for root, dirs, files in os.walk(Misc.const.DATADIR):
            for name in files:
                o = optpat.match(root)
                if o:
                    #option
                    (dt, type, barwidth, ul, expiry_y, expiry_m, expiry_d,strike) = o.groups(0)
                    if ul != "DEMO" and ul != "CTLT":
                        expiry_d = expiry_y+expiry_m+expiry_d

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
                            ctrct = self.model.brkConnection.make_contract(ul, dt, "USD", "SMART", expiry_d,strike)
                            contracts.append(ctrct)
                            newest[ctrct]={}
                            newest[ctrct]["c"] = datetime.datetime.strptime("19700101", "%Y%m%d")
                            newest[ctrct]["t"] = type
                else:
                    s = stkpat.match(root)
                    if s:
                        (dt, type, barwidth, ul) = s.groups(0)

                        if ul != "DEMO":
                            if dt not in latest:
                                latest[dt]={}
                            if type not in latest[dt]:
                                latest[dt][type] = {}
                            if barwidth not in latest[dt][type]:
                                latest[dt][type][barwidth] = {}
                            if ul not in latest[dt][type][barwidth]:
                                latest[dt][type][barwidth][ul] = {}

                                ctrct = self.model.brkConnection.make_contract(ul, dt, "USD", "SMART")
                                contracts.append(ctrct)
                                newest[ctrct]={}
                                newest[ctrct]["c"] = datetime.datetime.strptime("19700101", "%Y%m%d")
                                newest[ctrct]["t"] = type


                m = re.match(r"^(....)(..)(..)\.csv", name)
                if m:
                    y,m,d = m.groups(0)

                    if newest[ctrct]["c"] < datetime.datetime.strptime(y + m + d,"%Y%m%d"):
                            newest[ctrct]["c"] = datetime.datetime.strptime(y+m+d, "%Y%m%d")
                            newname = datetime.datetime.strftime(newest[ctrct]["c"], "%Y%m%d")+".csv"
                            nextname = datetime.datetime.strftime(newest[ctrct]["c"]+datetime.timedelta(1), "%Y%m%d")+".csv"
                            #newestname[ctrct]["f"] = os.path.join(root,name)
                            newest[ctrct]["f"] = os.path.join(root,nextname)

        with open("downloadOptions.ps1","w") as f:
            for ctrct in newest:
                newestdate=newest[ctrct]["c"].date()
                today = datetime.datetime.today().date()
                csvfile = newest[ctrct]["f"]
                if  today > newestdate+datetime.timedelta(1):
    #            if datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(1),"%Y%m%d") > datetime.datetime.strftime(newestdate, "%Y%m%d"):
                    #print("rm "+newest[ctrct]["f"])
                    if not os.path.exists(csvfile):
                        startdate = datetime.datetime.strftime(newestdate, "%Y%m%d")
                        enddate = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
                        if startdate != enddate:
                            if ctrct.secType == "OPT":
                                f.write('py .\download.py --port "4002" --security-type "OPT" --size "1 min" '+
                                      ' --start-date '+ startdate +
                                      ' --end-date '+ enddate +
                                      ' --data-type ' +  newest[ctrct]["t"] +
                                      ' --expiry '+ ctrct.lastTradeDateOrContractMonth +
                                      ' --strike ' + ctrct.strike +
                                      '  ' + ctrct.symbol+"\n")
                            else:
                                f.write('py .\download.py --port "4002" --security-type "STK" --size "1 min" ' +
                                      ' --start-date '+ startdate +
                                      ' --end-date '+ enddate +
                                      ' --data-type ' +  newest[ctrct]["t"] +
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
