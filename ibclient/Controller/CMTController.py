import os
import re
import datetime

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
        for root, dirs, files in os.walk("data"):
            for name in files:
                r = re.match(r"data\\(...)_(.+)\\(.....)\\(\w*)(....)(..)(..)C(.+)$", root)
                if r:
                    #option
                    (dt, type, barwidth, ul, expiry_y, expiry_m, expiry_d,strike) = r.groups(0)
                    expiry_d = expiry_y+expiry_m+expiry_d

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
                        ctrct = self.model.brkConnection.make_contract(ul, "OPT", "USD", "SMART", expiry_d,strike)
                        contracts.append(ctrct)
                        newest[ctrct]={}
                        newest[ctrct]["c"] = datetime.datetime.strptime("19700101", "%Y%m%d")
                        newest[ctrct]["t"] = type

                m = re.match(r"^(....)(..)(..)\.csv", name)
                if m:
                    y,m,d = m.groups(0)

                    # if latest[dt][type][barwidth][ul][expiry_d][strike] < datetime.datetime.strptime(y+m+d, "%Y%m%d"):
                    if newest[ctrct]["c"] < datetime.datetime.strptime(y + m + d,"%Y%m%d"):
                            newest[ctrct]["c"] = datetime.datetime.strptime(y+m+d, "%Y%m%d")


                        # latest[dt][type][barwidth][ul][expiry_d][strike] = datetime.datetime.strptime(y+m+d, "%Y%m%d")

            # for c in contracts:
            #     app = DownloadApp(contracts, args)
            #     app.connect("127.0.0.1", args.port, clientId=0)
            #     app.run()

            for name in dirs:
                print(os.path.join(root, name))
        for ctrct in newest:
            newestdate=newest[ctrct]["c"]+datetime.timedelta(1)
            if datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d") != datetime.datetime.strftime(newestdate, "%Y%m%d"):
                print('py .\download.py --port "4002" --security-type "OPT" --size "1 min" --start-date '+
                      datetime.datetime.strftime(newestdate, "%Y%m%d")+
                      ' --end-date '+ datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d")+
                      ' --data-type ' +  newest[ctrct]["t"] +
                      ' --expiry '+ ctrct.lastTradeDateOrContractMonth +
                      ' --strike ' + ctrct.strike +
                      '  ' + ctrct.symbol)

            print('py .\download.py --port "4002" --security-type "STK" --size "1 min" --start-date '+
                  datetime.datetime.strftime(datetime.datetime.strptime("20200701","%Y%m%d"), "%Y%m%d")+
                  ' --end-date '+ datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d")+
                  ' --data-type ' +  newest[ctrct]["t"] +
                  '  ' + ctrct.symbol)

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
