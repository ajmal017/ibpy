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
        if lc in [6,7,9,10,11,12,13,14,15,16,17,18]:
            try:
                a = self.sourceModel().data(left, role)
                b = self.sourceModel().data(right, role)
                return float(a) < float(b)
            except:
                return False
        elif lc in [1,2,3,4,5]:
            return (str(self.sourceModel().data(left, role))) < str((self.sourceModel().data(right, role)))
        elif lc == 17:
            try:
                a = float(self.sourceModel().data(left, role).replace("%",""))
                b = float(self.sourceModel().data(right, role).replace("%",""))
                return a < b
            except:
                return False
        else:
            return False;

class CMTModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.my_signal = pyqtSignal()
        self.mylist = mylist
        self.header = header
        self.timer = QtCore.QTimer()
        self.change_flag = True
        self.timer.timeout.connect(self.updateModel)
        self.timer.start(1000)
        self.ccdict = {}
        self.bw = {}

        self.background_colors = [QtGui.QColor(QtCore.Qt.green), QtGui.QColor(QtCore.Qt.yellow), QtGui.QColor(QtCore.Qt.red)]

        # self.rowCheckStateMap = {}

    def setCCList(self, ccd):
        self.ccdict = ccd

    def setAutoUpdate(self, value):
        if value == True:
            self.timer.start(1000)
        else:
            self.timer.stop()

    def setDataList(self, mylist):
        self.mylist = mylist
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def updateModel(self):
        dataList2 = []

        summary = []
        for colidx, bw in enumerate(self.ccdict["coveredCalls"]["bw"]):
            summary.append(0)

        for rowidx,bw in enumerate(self.ccdict["coveredCalls"]["bw"]):
            if int(bw["tickerId"]) % 2 == 0:
                if const.LASTPRICE in globvars.tickerData[bw["tickerId"]]:
                    tv = bw["cc"].getTimevalue()
                    itv = bw["itv"]

                    summary[15] += tv

                    if (float(bw["option"]["@strike"]) > float(bw["cc"].get_stk_price())):
                        ioanow = "OTM"
                    elif (float(bw["option"]["@strike"]) < float(bw["cc"].get_stk_price())):
                        ioanow = "ITM"
                    else:
                        ioanow = "ATM"

                    if bw["ioa_initial"] == ioanow:
                        ioastate = ioanow
                    else:
                        ioastate = bw["ioa_initial"] + "=>" + ioanow

                    change = globvars.tickerData[bw["tickerId"]][const.LASTPRICE] - float(bw["underlyer"]["@price"])
                    changepct = 100*(globvars.tickerData[bw["tickerId"]][const.LASTPRICE] - float(bw["underlyer"]["@price"]))/float(bw["underlyer"]["@price"])

                    dataList2.append([QCheckBox(bw["underlyer"]["@tickerSymbol"]),
                                      bw["cc"].get_industry(),
                                      bw["@quantity"] + " ("+str(int(int(bw["@quantity"])*float(bw["@enteringPrice"]))/10)+"K )",
                                      bw["cc"].get_strike(),
                                      bw["cc"].get_expiry() + " (" + str(bw["cc"].get_days())+" d)",
                                      ioastate,

                                      bw["underlyer"]["@price"],
                                      "{:.2f}".format(globvars.tickerData[bw["tickerId"]][const.LASTPRICE]),
                                      "{:.2f}".format(change),
                                      "{:>2.2f}".format(changepct),
                                      "{:.2f}".format(globvars.tickerData[bw["tickerId"]][const.BIDPRICE]),
                                      "{:.2f}".format(globvars.tickerData[bw["tickerId"]][const.ASKPRICE]),

                                      "{:.2f}".format(globvars.tickerData[str(int(bw["tickerId"])+1)][const.LASTPRICE]),
                                      "{:.2f}".format(globvars.tickerData[str(int(bw["tickerId"])+1)][const.BIDPRICE]),
                                      "{:.2f}".format(globvars.tickerData[str(int(bw["tickerId"])+1)][const.ASKPRICE]),

                                      "{:.2f}".format(itv),
                                      "{:.2f}".format(itv*int(bw["@quantity"])*100),
                                      "{:.2f}".format(tv),
                                      "{:.2f}".format(tv*int(bw["@quantity"])*100),
                                      "{:.2f}".format(100*tv/itv)])
                    if globvars.tickerData[bw["tickerId"]][const.LASTPRICE] > 0.01 and globvars.tickerData[str(int(bw["tickerId"])+1)][const.LASTPRICE] > 0.01:
                        summary[16] += tv*int(bw["@quantity"])*100
                        summary[14] += itv*int(bw["@quantity"])*100
                    else:
                        ulbid = globvars.tickerData[bw["tickerId"]][const.BIDPRICE]
                        ulask = globvars.tickerData[bw["tickerId"]][const.ASKPRICE]
                        opbid = globvars.tickerData[str(int(bw["tickerId"])+1)][const.BIDPRICE]
                        opask = globvars.tickerData[str(int(bw["tickerId"]) + 1)][const.ASKPRICE]
                        if opask+opbid > 0.01:
                            spread = (2*(opask-opbid)/(opask+opbid))
                            if ulbid > 0.01 and opbid > 0.01 and ulask > 0.01 and opask > 0.01 and spread < 0.25:
                                bw["cc"].set_stk_price((ulask+ulbid)/2)
                                bw["cc"].set_opt_price((opask+opbid)/2)
                                tv = bw["cc"].getTimevalue()
                                summary[16] += tv * int(bw["@quantity"]) * 100
                                summary[14] += itv * int(bw["@quantity"]) * 100

        globvars.tvprofit = int(summary[14])-int(summary[16])



        dataList2.append([QCheckBox(""),
                          "",
                          0,
                          0,
                          "",
                          "",

                          "",
                          "",
                          "",
                          "",
                          "",
                          "",

                          "",
                          "",
                          "",

                          "",
                          summary[14],
                          "",
                          summary[16],
                          ""])


        self.mylist = dataList2
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        if (index.column() == 0):
            value = self.mylist[index.row()][index.column()].text()
            try:
                self.bw = globvars.symbol[value]
            except:
                print("ERROR")
        else:
            a = index.row()
            b = index.column()

            value = self.mylist[a][b]

        if role == QtCore.Qt.EditRole:
            return value

        elif role == QtCore.Qt.BackgroundRole:
            ix = self.index(index.row(), index.column())
            cellvalue = ix.data()
            color = self.background_colors[1]
            # if index.column() == 12:
            #     try:
            #         if float(cellvalue) > 0.01:
            #             #self.setData(index(index.row(), 0), QtGui.QBrush(QtCore.Qt.red), QtCore.Qt.BackgroundRole)
            #             color = self.background_colors[0]
            #         else:
            #             color = self.background_colors[1]
            #     except:
            #         return self.background_colors[1]
            # else:
            if self.bw != None:
                if "cc" in self.bw:
                    a = float(self.bw["cc"].get_stk_price())
                    b = float(self.bw["@enteringPrice"])
                    if  a > 0.5 and a <= b:
                        color = self.background_colors[2]

            #pix = QtCore.QPersistentModelIndex(ix)
            return color

        elif role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                if self.mylist[index.row()][index.column()].isChecked():
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def flags(self, index):
        if not index.isValid():
            return None
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
                self.mylist[index.row()][index.column()].setChecked(True)
                self.mylist[index.row()][index.column()].setText("C")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])
            else:
                self.mylist[index.row()][index.column()].setChecked(False)
                self.mylist[index.row()][index.column()].setText("D")
        else:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        print(">>> setData() index.row = ", index.row())
        print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True
