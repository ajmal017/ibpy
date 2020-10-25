import os
import xmltodict
from datetime import datetime
import pandas as pd
import argparse

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

import matplotlib.dates as mdates

from Misc.globals import globvars
from Misc import const
from Controller.covcall import covered_call
from .BrkConnection import BrkConnection
from .Account import Account
from Color import PALETTES_NAMED, hex2rgb, rgb2hex
from .download import DownloadApp, make_download_path
from .resamplecsv import resample


class Summary():
    def __init__(self):
        self.total = 0
        self.totalitv = 0
        self.totalctv = 0

    def set_total(self,t):
        self.total = t

    def get_total(self,t):
        return self.total

class PrxyModel(QSortFilterProxyModel):

    def __init__(self):
        super().__init__()
        self.invalidateFilter()

    def lessThan(self, left, right):
        role = QtCore.Qt.DisplayRole
        lc = left.column()
        if lc in [
                const.COL_ID                    ,
                const.COL_ROLLED                ,
                const.COL_POSITION              ,
                const.COL_CAPPART               ,
                const.COL_DURATION              ,
                const.COL_STRIKE                ,
                const.COL_STATUS                ,
                const.COL_ULINIT                ,
                const.COL_BWPRICE                ,
                const.COL_BWPNOW                 ,
                const.COL_BWPPROF                ,
                const.COL_BWPPL                  ,
                const.COL_ULLAST                 ,
                const.COL_ULLMINUSBWP            ,
                const.COL_ULLMINUSSTRIKE         ,
                const.COL_ULLCHANGE              ,
                const.COL_ULLCHANGEPCT           ,
                const.COL_ULBID                  ,
                const.COL_ULASK                  ,
                const.COL_OPLAST                 ,
                const.COL_OPBID                  ,
                const.COL_OPASK                  ,
                const.COL_INITINTRNSCVAL         ,
                const.COL_INITINTRNSCVALDOLL     ,
                const.COL_INITTIMEVAL            ,
                const.COL_INITTIMEVALDOLL        ,
                const.COL_CURRINTRNSCVAL         ,
                const.COL_CURRINTRNSCVALDOLL     ,
                const.COL_CURRTIMEVAL            ,
                const.COL_CURRTIMEVALDOLL        ,
                const.COL_DOWNSIDEPROTECTPCT     ,
                const.COL_UPSIDEPOTENTIALPCT     ,
                const.COL_TIMEVALCHANGEPCT       ,
                const.COL_TIMEVALPROFIT          ,
                const.COL_REALIZED               ,
                const.COL_ULUNREALIZED           ,
                const.COL_TOTAL                  ]:
            try:
                a = self.sourceModel().data(left, role)
                b = self.sourceModel().data(right, role)
                return float(a) < float(b)
            except:
                return False
        else:
            return (str(self.sourceModel().data(left, role))) < str((self.sourceModel().data(right, role)))


    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()  # the underlying model,

        index = model.index(source_row, const.COL_POSITION, source_parent)

        cc = model.bwl[str(((index.row() * 2) + const.INITIALTTICKERID))]

        if model.includeZeroPositions == False and cc.statData.position == 0:
            if cc.statData.buyWrite["underlyer"]["@tickerSymbol"] != "DEMO":
                return False

        return True


class CMTModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    def __init__(self, *args):
        QAbstractTableModel.__init__(self, *args)
        self.account  = Account()
        self.args = argparse.Namespace()
        self.bwl = {}
        self.includeZeroPositions = True
        self.summary = Summary()
        self.summary.overallMarketValue = 0
        self.candleWidth = const.CANDLEWIDTH1
        self.brkConnection = BrkConnection()

    def initData(self, c):
        self.controller = c

        with open('C:/git/ibpy/ibclient/Config/cc.xml') as fd:
            ccdict = xmltodict.parse(fd.read())

        tickerId = const.INITIALTTICKERID
        for bw in ccdict["coveredCalls"]["bw"]:
            #if "closed" in bw and bw["@name"] != "DEMO":
            self.bwl[str(tickerId)] = covered_call(bw, tickerId)
            self.bwl[str(tickerId+1)] = self.bwl[str(tickerId)]
            tickerId = tickerId + 2

        self.brkConnection.setData(self.bwl, self.account)
        self.ccdict = {}
        self.startModelTimer()

    def changeBrokerPort(self,newport):
        self.brkConnection.changeBrokerPort(newport)

    def connectBroker(self):
        self.brkConnection.connectToIBKR()

    def disconnectBroker(self):
        if globvars.connectionState == "CONNECTED":
            self.brkConnection.disconnectFromIBKR()

    def getHistStockData(self, cc):
        cc.histData = []
        optQueryList = []
        optionQuery = {}
        raStart = {}
        nowstr = datetime.strftime(datetime.now(), "%Y%m%d")
        raStart['to'] = cc.statData.buyWrite["option"]["@expiry"]
        raStart['strike'] = cc.statData.buyWrite["option"]["@strike"]
        raStart['sellprice'] = cc.statData.buyWrite["option"]["@price"]
        ulsym = cc.statData.buyWrite["underlyer"]["@tickerSymbol"]
        dfDataList = []
        contractsToDownload = []
        stockPath = os.path.join(os.path.join(const.DATADIR,"STK_MIDPOINT"), self.candleWidth ,cc.statData.buyWrite["underlyer"]["@tickerSymbol"])
        if os.path.exists(stockPath) and len(os.listdir(stockPath)) > 0:
            files = os.listdir(os.path.join(os.path.join(const.DATADIR,"STK_MIDPOINT"), self.candleWidth ,cc.statData.buyWrite["underlyer"]["@tickerSymbol"]))
            for file in files:
                filetmp = os.path.join(os.path.join(const.DATADIR,"STK_MIDPOINT"),self.candleWidth,cc.statData.buyWrite["underlyer"]["@tickerSymbol"], file)
                tmpdf = pd.read_csv(filetmp, index_col=0, parse_dates=True)
                #filter out outside RTH times as we have too many outliers otherwise:
                dt = file.split(".")
                dtstart = dt[0]+" 15:30:00"
                dtend = dt[0]+" 21:59:00"
                tmpdf = tmpdf[dtstart:dtend]
                dfDataList.append(tmpdf)

            stockData = pd.concat(dfDataList)
        else:
            orgStockPath = os.path.join(os.path.join(const.DATADIR,"STK_MIDPOINT"), "1_min" ,cc.statData.buyWrite["underlyer"]["@tickerSymbol"])
            if not os.path.exists(orgStockPath) or len(os.listdir(orgStockPath)) == 0:
                ctrct = cc.underlyer()
                self.args.base_directory = const.DATADIR
                self.args.security_type = ctrct.secType
                self.args.data_type = "MIDPOINT"
                self.args.size = "1 min"
                self.args.max_days = None
                self.args.start_date = datetime.strptime("20200501","%Y%m%d")
                self.args.end_date = datetime.today()
                self.args.duration = "1 D"
                self.args.port = self.controller.brokerPort
                p = make_download_path(self.args,ctrct)
                os.makedirs(p, exist_ok=True)
                contractsToDownload.append(ctrct)
                downApp = DownloadApp(contractsToDownload, self.args)
                downApp.connect("127.0.0.1", self.controller.brokerPort, clientId=10)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("This is a message box")
                downApp.run()
            resample(False, cc.statData.buyWrite["underlyer"]["@tickerSymbol"])
            # print('py Model\download.py --port "7495" --security-type "STK" --size "1 min"  --start-date 20200501 --end-date ' + nowstr + " --data-type MIDPOINT " + ulsym)
            stockData = None

        if len(cc.statData.rollingActivity) == 0:
            optionQuery["Contract"] = cc.getInitialOption()
            optionQuery['OpeningTime'] = cc.statData.enteringTime
            optQueryList.append(optionQuery)
        else:
            for i, ra in enumerate(cc.statData.rollingActivity):
                if i == 0:
                    optionQuery["Contract"] = cc.getRolledOption(raStart)
                    optionQuery['ClosingTime'] = ra["when"]
                    optionQuery['OpeningTime'] = cc.statData.enteringTime
                    optQueryList.append(optionQuery)

                    nextOptionQuery = {}
                    nextOptionQuery["Contract"] = cc.getRolledOption(ra)
                    nextOptionQuery['OpeningTime'] = ra["when"]
                    optQueryList.append(nextOptionQuery)
                else:
                    optQueryList[-1]['ClosingTime'] = ra["when"]
                    nextOptionQuery = {}
                    nextOptionQuery['OpeningTime'] = ra["when"] #optQueryList[i-1]['ClosingTime']
                    nextOptionQuery["Contract"] = cc.getRolledOption(ra)
                    optQueryList.append(nextOptionQuery)

        if len(optQueryList) > 0:
            if cc.statData.exitingTime != "":
                optQueryList[-1]['ClosingTime'] = cc.statData.buyWrite["closed"]["@exitingTime"]
            else:
                optQueryList[-1]['ClosingTime'] = datetime.now().strftime("%Y%m%d %H:%M:%S")

        optiondata = {}
        for optionContract in optQueryList:
            expiry = optionContract["Contract"].lastTradeDateOrContractMonth
            strike = optionContract["Contract"].strike
            symbol = optionContract["Contract"].symbol
            optionname= symbol+expiry+"C"+strike
            path = os.path.join(os.path.join(const.DATADIR,"OPT_MIDPOINT"),self.candleWidth,optionname)
            if os.path.exists(path) and len(os.listdir(path)) > 0:
                files=os.listdir(path)
                dfDataList = []
                for file in files:
                    file = os.path.join(path, file)
                    df = pd.read_csv(file, index_col=0, parse_dates=True)
                    dfDataList.append(df)
                if len(files) > 0:
                    dfall = pd.concat(dfDataList)
                    optiondata[optionname] = dfall[optionContract["OpeningTime"]: optionContract["ClosingTime"]]
            else:
                orgpath = os.path.join(os.path.join(const.DATADIR,"OPT_MIDPOINT"),"1_min",optionname)
                if not os.path.exists(orgpath) or len(os.listdir(orgpath)) == 0:
                    if datetime.strptime(expiry,"%Y%m%d") > datetime.now():
                        #IB speichert keine alten Optionsdaten
                        ctrct = optionContract["Contract"]
                        self.args.base_directory = const.DATADIR
                        self.args.security_type = ctrct.secType
                        self.args.data_type = "MIDPOINT"
                        self.args.size = "1 min"
                        self.args.max_days = None
                        self.args.start_date = datetime.strptime("20200501", "%Y%m%d")
                        self.args.end_date = datetime.today()
                        self.args.duration = "1 D"
                        self.args.expiry =  expiry
                        self.args.strike = strike
                        self.args.port = self.controller.brokerPort
                        p = make_download_path(self.args, ctrct)
                        os.makedirs(p, exist_ok=True)
                        contractsToDownload.append(ctrct)
                        downApp = DownloadApp(contractsToDownload, self.args)
                        downApp.connect("127.0.0.1", self.controller.brokerPort, clientId=10)
                        downApp.run()
                    resample(False, symbol)
                    # print(path, 'py Model\download.py --port "7495" --security-type "OPT" --size "1 min"  --start-date 20200701 --end-date '+nowstr+ " --data-type MIDPOINT --expiry "+expiry+" --strike "+strike+" "+symbol)
                    #optiondata = None

        if optiondata is not None:
            if len(optiondata) > 0:
                cc.ophistData = pd.concat(optiondata)
            else:
                cc.ophistData = optiondata
        else:
            cc.ophistData = None

        if stockData is not None:
            cc.histData = stockData[cc.statData.enteringTime:]
        else:
            cc.histData = None

        return [(q["OpeningTime"], float(q["Contract"].strike)) for q in optQueryList]

    def startModelTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateModel)
        self.timer.start(1000)

    def setCCList(self, ccd):
        self.ccdict = ccd

    def setAutoUpdate(self, value):
        if value == True:
            self.timer.start(1000)
        else:
            self.timer.stop()

    def updateModel(self):
        globvars.tvprofit = 0
        k = list(self.bwl.keys())[0]

        sum = []
        for i,d in enumerate(self.bwl[k].dispData):
            sum.append(0.0)

        for cc in self.bwl:
            self.bwl[cc].updateData()

        a = []
        for s in sum:
            a.append("{:.2f}".format(s))

        self.summary.total    = 0
        self.summary.totalctv = 0
        self.summary.totalitv = 0
        self.summary.marketValue = 0

        for pos in self.bwl.keys():
            if int(pos) % 2 == 0:
                self.summary.total = self.summary.total + self.bwl[pos].total
                self.summary.marketValue = self.summary.marketValue + self.bwl[pos].currentMarketValue()
                self.bwl[pos].setOverallMarketValue(self.summary.overallMarketValue)
                c = self.bwl[pos].ctv()
                i = self.bwl[pos].statData.itv()
                p = self.bwl[pos].statData.position
                self.summary.totalctv = self.summary.totalctv + c * p * 100
                self.summary.totalitv = self.summary.totalitv + i * p * 100

        self.summary.overallMarketValue =  self.summary.marketValue

        globvars.total = self.summary.total
        globvars.totalCtv = self.summary.totalctv
        globvars.totalItv = self.summary.totalitv

        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))

    def rowCount(self, parent):
        return int(len(self.bwl.keys())/2)

    def columnCount(self, parent):
        k = list(self.bwl.keys())[0]
        return len(self.bwl[k].dispData)


    def data(self, index, role):

        if not index.isValid():
            globvars.logger.info("data: index not valid")
            return None

        r = index.row()
        c = index.column()


        cc = self.bwl[str(((index.row() * 2) + const.INITIALTTICKERID))]

        if role == QtCore.Qt.BackgroundRole:

            pat = Qt.SolidPattern

            if c == const.COL_ULLAST or c == const.COL_OPLAST:
                pat = Qt.DiagCrossPattern
                coltup = hex2rgb(globvars.colors['grau'])
                return QBrush(QColor.fromRgb(coltup[0],coltup[1],coltup[2]), pat)
                #return QBrush(QtCore.Qt.gray, pat)
            elif (c == const.COL_OPLAST and cc.oplastcalculated) or (c == const.COL_SYMBOL and cc.uncertaintyFlag):
                pat = Qt.CrossPattern

            if cc.is_valid():
                if cc.tickData.ullst < cc.statData.inibwprice:
                    #below breakeven
                    coltup = hex2rgb(globvars.colors['red'])
                    return QBrush(QColor.fromRgb(coltup[0], coltup[1], coltup[2]), pat)
                    #return QBrush(QtCore.Qt.red, pat)
                elif cc.tickData.ullst < cc.statData.strike:
                    #below strike
                    coltup = hex2rgb(globvars.colors['orange'])
                    return QBrush(QColor.fromRgb(coltup[0], coltup[1], coltup[2]), pat)
                    #return QBrush(QColor(255, 100, 100, 200), pat)
                else:
                    #otherwise we are green...
                    coltup = hex2rgb(globvars.colors['green'])
                    return QBrush(QColor.fromRgb(coltup[0], coltup[1], coltup[2]), pat)
#                    return QBrush(QtCore.Qt.green, pat)
            else:
                #data not valid for whatever reasons
                if cc.uncertaintyFlag == True:
                    pat = Qt.Dense6Pattern
                return QBrush(QtCore.Qt.gray, pat)

            coltup = hex2rgb(globvars.colors['braun'])
            return QBrush(QColor.fromRgb(coltup[0], coltup[1], coltup[2]), pat)

        elif role == QtCore.Qt.DisplayRole:
            value = self.bwl[str(((index.row()*2)+const.INITIALTTICKERID))].dispData[index.column()]
            return value

        elif role == QtCore.Qt.ToolTipRole:
            cc = self.bwl[str(((index.row()*2)+const.INITIALTTICKERID))]

            if c == const.COL_STRIKE:
                s = cc.statData.buyWrite["underlyer"]["@tickerSymbol"] + cc.statData.buyWrite["option"]["@expiry"] + " "
                s += "IROO:"
                s += "{:.2f}".format(cc.statData.itv())+" "
                s += "Price: " + "{:.2f}".format(cc.statData.inibwprice)
                try:
                    s += " = " + "{:.2f}".format(100*float(cc.statData.itv()) / float(cc.statData.inibwprice)) + " %"
                except:
                    pass

                if cc.statData.strike < cc.statData.inistkprice:
                    s += " ITM: Downside protection of " + "{:.2f}".format(100*float((cc.statData.inistkprice - cc.statData.strike)/cc.statData.inistkprice))+" % "
                else:
                    s += " OTM: Upside Potential of " + "{:.2f}".format(100*float((cc.statData.strike - cc.statData.inistkprice) / cc.statData.inistkprice)) + " % "

                return s
 #       globvars.lock.release()

    def headerData(self, col, orientation, role):
        headerlist = list(globvars.header1.keys())
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headerlist[col]

        elif role == QtCore.Qt.ToolTipRole:
            if col == 37:
                return globvars.total
            else:
                return globvars.header1[list(globvars.header1.keys())[col]]

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        # print(">>> flags() index.column() = ", index.column())
        if index.column() == 0:
            # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def getNumPositions(self):
        #one less because of demo position
        if self.includeZeroPositions == True:
            tmplst = self.bwl
        else:
            tmplst = [cc for cc in self.bwl if self.bwl[cc].statData.position > 0]
        return int((len(tmplst)/2))
