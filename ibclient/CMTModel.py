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
        if lc in [0,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]:
            try:
                a = self.sourceModel().data(left, role)
                b = self.sourceModel().data(right, role)
                return float(a) < float(b)
            except:
                return False
        elif lc in [1,2,3,4,5,6]:
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

    def __init__(self, parent, mylist, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.my_signal = pyqtSignal()
        self.buywrites = mylist
        self.header = globvars.header

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

        for cc in globvars.bwl:
            self.buywrites.append(cc.table_data())

            globvars.tvprofit = globvars.tvprofit + cc.tvprof()

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

            if c == 12:
                pat = Qt.DiagCrossPattern
                return QBrush(QtCore.Qt.gray, pat)

            if c == 19 and cc.oplastcalculated:
                pat = Qt.CrossPattern

            globvars.logger.info("")
            if cc.is_valid():
                if cc.tickerData["ullst"] < cc.inibwprice:
                    return QBrush(QtCore.Qt.darkRed, pat)
                elif cc.tickerData["ullst"] < cc.strike:
                    return QBrush(QtCore.Qt.red, pat)
                else:
                    return QBrush(QtCore.Qt.green, pat)
            else:
                return QBrush(QtCore.Qt.white, pat)

        elif role == QtCore.Qt.DisplayRole:
            value = self.buywrites[index.row()][index.column()]
            return value
        elif role == QtCore.Qt.ToolTipRole:
            return str(index.column())


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
