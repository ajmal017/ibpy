import xmltodict

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

from Misc.globals import globvars
from Misc import const
from Controller.covcall import covered_call
from .BrkConnection import BrkConnection
from .Account import Account

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

class CMTModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    def __init__(self, *args):
        QAbstractTableModel.__init__(self, *args)
        self.account  = Account()
        self.bwl = {}
        self.summary = Summary()
        self.brkConnection = BrkConnection()

    def initData(self, c):
        self.controller = c

        with open('Config/cc.xml') as fd:
            ccdict = xmltodict.parse(fd.read())

        tickerId = const.INITIALTTICKERID
        for bw in ccdict["coveredCalls"]["bw"]:
            if "closed" in bw:
                continue
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
        self.brkConnection.getStockData(cc)

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
#        globvars.lock.acquire()
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

        for pos in self.bwl.keys():
            if int(pos) % 2 == 0:
                self.summary.total = self.summary.total + self.bwl[pos].total
                c = self.bwl[pos].ctv()
                i = self.bwl[pos].statData.itv()
                p = self.bwl[pos].statData.position
                self.summary.totalctv = self.summary.totalctv + c * p * 100
                self.summary.totalitv = self.summary.totalitv + i * p * 100

        globvars.total = self.summary.total
        globvars.totalCtv = self.summary.totalctv
        globvars.totalItv = self.summary.totalitv

        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()
#        globvars.lock.release()

    def rowCount(self, parent):
        return int(len(self.bwl.keys())/2)

    def columnCount(self, parent):
        k = list(self.bwl.keys())[0]
        return len(self.bwl[k].dispData)


    def data(self, index, role):
#        globvars.lock.acquire()
        if not index.isValid():
            globvars.logger.info("data: index not valid")
            return None

        r = index.row()
        c = index.column()

        if role == QtCore.Qt.BackgroundRole:
            # globvars.logger.info("")

            cc = self.bwl[str(((index.row()*2)+const.INITIALTTICKERID))]

            pat = Qt.SolidPattern

            if c == const.COL_ULLAST or c == const.COL_OPLAST:
                pat = Qt.DiagCrossPattern
                return QBrush(QtCore.Qt.gray, pat)
            elif (c == const.COL_OPLAST and cc.oplastcalculated) or (c == const.COL_SYMBOL and cc.uncertaintyFlag):
                pat = Qt.CrossPattern

            if cc.is_valid():
                if cc.tickData.ullst < cc.statData.inibwprice:
                    #below breakeven
                    return QBrush(QtCore.Qt.red, pat)
                elif cc.tickData.ullst < cc.statData.strike:
                    #below strike
                    return QBrush(QColor(255, 100, 100, 200), pat)
                else:
                    #otherwise we are green...
                    return QBrush(QtCore.Qt.green, pat)
            else:
                #data not valid for whatever reasons
                if cc.uncertaintyFlag == True:
                    pat = Qt.Dense6Pattern
                return QBrush(QtCore.Qt.gray, pat)

            return QBrush(QtCore.Qt.gray, pat)

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

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
            if value == QtCore.Qt.Checked:
                self.buywrites[index.row()][index.column()].setChecked(True)
                self.buywrites[index.row()][index.column()].setText("C")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])
            else:
                self.buywrites[index.row()][index.column()].setChecked(False)
                self.buywrites[index.row()][index.column()].setText("D")
        else:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        print(">>> setData() index.row = ", index.row())
        print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True