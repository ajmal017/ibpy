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
        if left.column() in [2,5,6,7,8,9,10,11,12,13,14,15,16,17]:
            return float(self.sourceModel().data(left, role)) < float(self.sourceModel().data(right, role))
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

        for bw in self.ccdict["coveredCalls"]["bw"]:
            if int(bw["tickerId"]) % 2 == 0:
                if const.LASTPRICE in globvars.tickerData[bw["tickerId"]]:
                    tv = bw["cc"].getTimevalue()
                    itv = bw["itv"]

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
                                      bw["@quantity"],
                                      bw["cc"].get_strike(),
                                      bw["cc"].get_expiry() + " (" + str(bw["cc"].get_days())+" d)",
                                      ioastate,

                                      bw["underlyer"]["@price"],
                                      "{:.2f}".format(globvars.tickerData[bw["tickerId"]][const.LASTPRICE]),
                                      "{:.2f}".format(change),
                                      "{:>2.2f}".format(changepct)+" %",
                                      "{:.2f}".format(globvars.tickerData[bw["tickerId"]][const.BIDPRICE]),
                                      "{:.2f}".format(globvars.tickerData[bw["tickerId"]][const.ASKPRICE]),

                                      "{:.2f}".format(globvars.tickerData[str(int(bw["tickerId"])+1)][const.LASTPRICE]),
                                      "{:.2f}".format(globvars.tickerData[str(int(bw["tickerId"])+1)][const.BIDPRICE]),
                                      "{:.2f}".format(globvars.tickerData[str(int(bw["tickerId"])+1)][const.ASKPRICE]),

                                      "{:.2f}".format(itv),
                                      "{:.2f}".format(tv),
                                      "{:.2f}".format(tv*int(bw["@quantity"])*100),
                                      "{:.2f}".format(100*tv/itv)+" %"])

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
        else:
            value = self.mylist[index.row()][index.column()]
        if role == QtCore.Qt.EditRole:
            return value
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

    # def sort(self, col, order):
    #     """sort table by given column number col"""
    #     # print(">>> sort() col = ", col)
    #
    #     if col != 0:
    #         # self.mysignal.emit()
    #         #PYQTSIGNAL("layoutAboutToBeChanged()").emit()
    #         self.layoutAboutToBeChanged.emit()
    #         self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
    #         if order == Qt.DescendingOrder:
    #             self.mylist.reverse()
    #         self.layoutChanged.emit()

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
