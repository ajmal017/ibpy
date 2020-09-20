import operator  # used for sorting
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

from globals import globvars
import const

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

    def __init__(self, parent, mylist, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.my_signal = pyqtSignal()
        self.buywrites = mylist
        self.header = globvars.header1.keys()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateModel)
        self.timer.start(1000)
        self.ccdict = {}

    def setCCList(self, ccd):
        self.ccdict = ccd

    def setAutoUpdate(self, value):
        if value == True:
            self.timer.start(1000)
        else:
            self.timer.stop()

    def updateModel(self):
        self.buywrites = []

        globvars.tvprofit = 0

        sum = []
        for i,d in enumerate(globvars.bwl[0].table_data()):
            sum.append(0.0)

        for cc in globvars.bwl:
            if cc == globvars.bwl[-1]:
                data = sum
                self.buywrites.append(data)
            else:
                data = cc.table_data()
                self.buywrites.append(data)
                globvars.tvprofit = globvars.tvprofit + cc.tvprof()

                for  i,data_col in enumerate(data):
                    try:
                        if i in [
                            const.COL_INITINTRNSCVALDOLL,
                            const.COL_INITTIMEVALDOLL,
                            const.COL_CURRINTRNSCVALDOLL,
                            const.COL_CURRINTRNSCVAL,
                            const.COL_CURRINTRNSCVALDOLL,
                            const.COL_CURRTIMEVAL,
                            const.COL_CURRTIMEVALDOLL,
                            const.COL_TIMEVALCHANGEPCT,
                            const.COL_TIMEVALPROFIT,
                            const.COL_REALIZED,
                            const.COL_ULUNREALIZED,
                            const.COL_TOTAL
                        ]:
                            sum[i] = sum[i] + float(data_col)
                        elif i == const.COL_ULLAST:
                            sum[i] = sum[i] + cc.position * 100 * cc.tickerData["ullst"]
                        elif i == const.COL_OPLAST:
                            sum[i] = sum[i] + cc.position * 100 * cc.tickerData["oplst"]
                        elif i == const.COL_BWPRICE:
                            sum[i] = sum[i] + cc.position * 100 * float(cc.bw["@enteringPrice"])

                        else:
                            sum[i] = 0
                    except:
                        pass

        globvars.bwl[-1].set_summary(sum)

        a = []
        # for s in sum:
        #     a.append("{:.2f}".format(s))
        #
        # self.buywrites.append(a)

        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.buywrites)

    def columnCount(self, parent):
        return len(self.buywrites[0])


    def data(self, index, role):
        if not index.isValid():
            globvars.logger.info("data: index not valid")
            return None

        r = index.row()
        c = index.column()

        if len(globvars.bwl) < int(r):
            globvars.logger.error("buywrite member %i does not exist", r)
            return None

        # globvars.logger.info("row %i column %i role %i", r, c, role)

        cc = globvars.bwl[int(r)]

        # globvars.logger.info("")

        # if role == QtCore.Qt.EditRole:
        #     return value

            # globvars.logger.info("")

        if role == QtCore.Qt.BackgroundRole:
            # globvars.logger.info("")


            pat = Qt.SolidPattern

            if c == const.COL_ULLAST:
                pat = Qt.DiagCrossPattern
                return QBrush(QtCore.Qt.gray, pat)

            if c == const.COL_OPLAST and cc.oplastcalculated:
                pat = Qt.CrossPattern

            if c == const.COL_OPLAST:
                pat = Qt.DiagCrossPattern
                return QBrush(QtCore.Qt.gray, pat)

            if (c == 34 and r == 21):
                return QBrush(QtCore.Qt.yellow, Qt.SolidPattern)

            if c == 1 and cc.uncertaintyFlag:
                pat = Qt.CrossPattern

            if cc.is_valid():
                if cc.tickerData["ullst"] < cc.inibwprice:
                    return QBrush(QtCore.Qt.darkRed, pat)
                elif cc.tickerData["ullst"] < cc.strike:
                    return QBrush(QtCore.Qt.red, pat)
                else:
                    return QBrush(QtCore.Qt.green, pat)
            else:
                if cc.uncertaintyFlag == True:
                    pat = Qt.Dense6Pattern

                return QBrush(QtCore.Qt.gray, pat)

        elif role == QtCore.Qt.DisplayRole:
            value = self.buywrites[index.row()][index.column()]
            return value

        elif role == QtCore.Qt.ToolTipRole:
            if c == 5:
                s = cc.symbol + cc.expiry + " "
                s += "IROO:"
                s += "{:.2f}".format(cc.itv())+" "
                s += "Price: " + "{:.2f}".format(cc.inibwprice)
                s += " = " + "{:.2f}".format(100*float(cc.itv()) / float(cc.inibwprice)) + " %"

                if cc.strike < cc.inistkprice:
                    s += " ITM: Downside protection of " + "{:.2f}".format(100*float((cc.inistkprice - cc.strike)/cc.inistkprice))+" % "
                else:
                    s += " OTM: Upside Potential of " + "{:.2f}".format(100*float((cc.strike - cc.inistkprice) / cc.inistkprice)) + " % "

                return s

            if c == 7:
                return cc.symbol + cc.expiry + " " + "time of this price was "+cc.ul_ts
            elif c == 1:
                if cc.uncertaintyFlag:
                    return cc.symbol + cc.expiry + " " + "Grosse Unsicherheit wegen unscharfem Optionspreis"
                else:
                    return cc.symbol + cc.expiry + " " + "Kleine Unsicherheit wegen relativ genauem Optionspreis"

            return cc.symbol + " " + cc.expiry + " " + str(index.column())+" "+str(index.row())


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
