''' pqt_tableview3.py
explore PyQT's QTableView Model
using QAbstractTableModel to present tabular data
allow table sorting by clicking on the header title
used the Anaconda package (comes with PyQt4) on OS X
(dns)
'''

# coding=utf-8

import operator  # used for sorting
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from time import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum
import logger as logger
from globals import globvars
from covcall import covered_call
import time
import xmltodict
import datetime
from globals import globvars
import const

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def historicalData(self, reqId, bar):
        if reqId not in bars:
            bars[reqId] = []
        print(reqId, "BarData.", bar)
        bars[reqId].append(bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        if reqId not in endflag:
            endflag[reqId] = False
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        endflag[reqId] = True

    def historicalDataUpdate(self, reqId: int, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)


    def tickPrice(self, reqId, tickType, value, attrib):
        tickerId = str(reqId)

        bw = tickerData[tickerId]["bw"]

        if str(tickType) == const.LASTPRICE :
            if reqId % 2 == 0:
                bw["cc"].set_stk_price(value)
            else:
                bw["cc"].set_opt_price(value)
            #print('The current last price of ', tickerData[tickerId]["bw"]["underlyer"]["@tickerSymbol"], " is ",value)
            tickerData[tickerId][const.LASTPRICE] = value
            #print('The currenttv of ', tickerData[tickerId]["bw"]["underlyer"]["@tickerSymbol"], " is ",bw["cc"].getTimevalue())


        if str(tickType) == const.ASKPRICE :
            #print('The last ask price of ', tickerData[tickerId]["bw"]["underlyer"]["@tickerSymbol"], " is ",value)
            tickerData[tickerId][const.ASKPRICE] = value

        if str(tickType) == const.BIDPRICE :
            #print('The last bid price of ', tickerData[tickerId]["bw"]["underlyer"]["@tickerSymbol"], " is ",value)
            tickerData[tickerId][const.BIDPRICE] = value

        # cc = covered_call(underlyer, "C", float(bw["option"]["@strike"]), date_time_obj)
        # cc.set_stk_price(tickerData[reqId]["underlyer"]["@price"])

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)


    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)


    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)


    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)

class MyWindow(QWidget):
    def __init__(self, dataList, header, *args):
        QWidget.__init__(self, *args)
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on the header to sort table")

        self.table_model = MyTableModel(self, dataList, header)
        self.table_view = QTableView()
        # self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        # bind cell click to a method reference
        self.table_view.clicked.connect(self.showSelection)
        self.table_view.clicked.connect(self.selectRow)

        self.table_view.setModel(self.table_model)
        # enable sorting
        self.table_view.setSortingEnabled(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def update_model(self, datalist, header):
        self.table_model2 = MyTableModel(self, dataList, header)
        self.table_view.setModel(self.table_model2)
        self.table_view.update()

    def showSelection(self, item):
        cellContent = item.data()
        # print(cellContent)  # test
        sf = "You clicked on {}".format(cellContent)
        # display in title bar for convenience
        self.setWindowTitle(sf)

    def selectRow(self, index):
        # print("current row is %d", index.row())
        pass

class MyTableModel(QAbstractTableModel):
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

        # self.rowCheckStateMap = {}

    def setDataList(self, mylist):
        self.mylist = mylist
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def updateModel(self):
        dataList2 = []

        # tickerData[bw["tickerId"]][const.LASTPRICE]

        for bw in ccdict["coveredCalls"]["bw"]:
            if int(bw["tickerId"]) % 2 == 0:
                if const.LASTPRICE in tickerData[bw["tickerId"]]:
                    tv = bw["cc"].getTimevalue()
                    itv = bw["itv"]
                    dataList2.append([QCheckBox(bw["underlyer"]["@tickerSymbol"]),

                                      "{:.2f}".format(tickerData[bw["tickerId"]][const.LASTPRICE]),
                                      "{:.2f}".format(tickerData[bw["tickerId"]][const.BIDPRICE]),
                                      "{:.2f}".format(tickerData[bw["tickerId"]][const.ASKPRICE]),

                                      "{:.2f}".format(tickerData[str(int(bw["tickerId"])+1)][const.LASTPRICE]),
                                      "{:.2f}".format(tickerData[str(int(bw["tickerId"])+1)][const.BIDPRICE]),
                                      "{:.2f}".format(tickerData[str(int(bw["tickerId"])+1)][const.ASKPRICE]),

                                    "{:.2f}".format(itv),"{:.2f}".format(tv), "{:.2f}".format(100*tv/itv), 0, 0, 0, 0, 'MA', '01',0])

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
                # print(">>> data() row,col = %d, %d" % (index.row(), index.column()))
                if self.mylist[index.row()][index.column()].isChecked():
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        # print(">>> sort() col = ", col)
        if col != 0:
            self.mysignal.emit()
            #PYQTSIGNAL("layoutAboutToBeChanged()").emit()
            self.layoutAboutToBeChanged.emit()
            self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self.mylist.reverse()
            self.layoutChanged.emit()

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
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
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

def timer_func(win, mylist):
    print(">>> timer_func()")
    win.table_model.setDataList(mylist)
    win.table_view.repaint()
    win.table_view.update()


# def timer_func(num):
#     print(">>> timer_func() num = ", num)

date_time_str = '2020-09-18 22:00:00.000000'
date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

date_time_str = '2020-09-18 22:00:00.000000'
date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

def run_loop():
    ibapp.run()

if __name__ == '__main__':
    globvars.init_globvars()
    mainLogger = logger.initMainLogger()
    initialtickerId = 4100
    tv = []
    itv = []
    tickerData = {}
    bars = {}
    endflag = {}

    with open('cc.xml') as fd:
        ccdict = xmltodict.parse(fd.read())

    app = QApplication([])
    ibapp = IBapi()
    ibapp.connect('127.0.0.1', 7495, 1)

    # you could process a CSV file to create this data
    header = ['Symbol', 'UL-Last', 'UL-Bid', 'UL-Ask', 'OP-Lst', 'OP-Bid', 'OP-Ask', 'ITV', 'CurTV', 'TV-Profit', 'Pending Action', '0', 'a', 'b', 'c', 'Expiry', 'd']
    # a list of (fname, lname, age, weight) tuples
    checkbox1 = QCheckBox("1");
    checkbox1.setChecked(True)
    dataList = [
        [checkbox1, '0', '0', '0', '0', '0', 0, 0, 0, 0, 0, 0, 0],
    ]

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    mainLogger.info('Started')
    tickerId = initialtickerId
    for bw in ccdict["coveredCalls"]["bw"]:

        (underlyer,option) = covered_call.get_contracts(bw)

        bw["cc"] = covered_call("Call", underlyer, bw["option"]["@strike"], bw["option"]["@expiry"])
        bw["itv"] = bw["cc"].calc_itv(bw)
        bw["ctv"] = bw["cc"].getTimevalue()
        bw["tvprof"] = bw["itv"] - bw["ctv"]
        bw["pac"] = ""

        dataList.append([QCheckBox(bw["underlyer"]["@tickerSymbol"]), bw["option"]["@strike"], bw["option"]["@expiry"], 0, 0, 0, 0, 0, 0, bw["itv"], bw["ctv"], bw["tvprof"], bw["pac"]])

        mainLogger.info("querying no. %s: %s", bw["@id"], bw["underlyer"]["@tickerSymbol"])

        bw["tickerId"] = str(tickerId)


        now = datetime.datetime.now()
        dt = now.strftime("%Y%m%d %H:%M:00")
        dt = now.strftime("%Y%m%d 22:00:00")

        # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
        # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
        #    app.reqHistoricalData(bw["tickerId"], option, dt, "60 S", "10 secs", "MIDPOINT", 1, 1, False, [])
        #    app.reqHistoricalData(bw["tickerId"]+1, underlyer, dt, "60 S", "10 secs", "MIDPOINT", 1, 1, False, [])

        bw["underlyer"]["tickerId"] = str(tickerId)
        bw["option"]["tickerId"] = str(tickerId+1)

        tickerData[bw["underlyer"]["tickerId"]] = {}
        tickerData[bw["option"]["tickerId"]] = {}

        tickerData[bw["underlyer"]["tickerId"]]["bw"] = bw
        tickerData[bw["option"]["tickerId"]]["bw"] = bw

        tickerData[bw["underlyer"]["tickerId"]][const.BIDPRICE] = 0
        tickerData[bw["underlyer"]["tickerId"]][const.ASKPRICE] = 0
        tickerData[bw["underlyer"]["tickerId"]][const.LASTPRICE] = 0

        tickerData[bw["option"]["tickerId"]][const.ASKPRICE] = 0
        tickerData[bw["option"]["tickerId"]][const.LASTPRICE] = 0
        tickerData[bw["option"]["tickerId"]][const.BIDPRICE] = 0

        ibapp.reqMktData(bw["underlyer"]["tickerId"], underlyer, "", False, False, [])
        ibapp.reqMktData(bw["option"]["tickerId"]   , option, "", False, False, [])

        tickerId += 2

    win = MyWindow(dataList, header)
    win.show()
    # win.table_model.setDataList(dataList)
    # timer = threading.Timer(10, timer_func, (win, dataList2))
    # timer.start()
    app.exec_()
