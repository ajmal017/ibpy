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
        if tickType == const.LASTPRICE :
            print('The current last price of ', tickerData[reqId]["underlyer"]["@tickerSymbol"], " is ",value)
            tickerData[reqId]["underlyer"][const.LASTPRICE] = value

        if tickType == const.ASKPRICE :
            print('The last ask price of ', tickerData[reqId]["underlyer"]["@tickerSymbol"], " is ",value)
            tickerData[reqId]["underlyer"][const.ASKPRICE] = value

        if tickType == const.BIDPRICE :
            print('The last bid price of ', tickerData[reqId]["underlyer"]["@tickerSymbol"], " is ",value)
            tickerData[reqId]["underlyer"][const.BIDPRICE] = value

        cc = covered_call(underlyer, "C", float(bw["option"]["@strike"]), date_time_obj)
        cc.set_stk_price(tickerData[reqId]["underlyer"]["@price"])

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

        for bw in ccdict["coveredCalls"]["bw"]:
            dataList2.append([QCheckBox(bw["underlyer"]["@tickerSymbol"]), int(100*tickerData[bw["tickerId"]]["underlyer"][const.LASTPRICE]),
                              str(100*tickerData[bw["tickerId"]]["underlyer"][const.BIDPRICE]), str(100*tickerData[bw["tickerId"]]["underlyer"][const.ASKPRICE]), 'cu1705,cu1710', 0, 0, 0, 0,
                            0,0, 0, 0, 0, 0, 0, 'MA', '01'])
            # dataList2.append([QCheckBox(bw["option"]["@tickerSymbol"]), int(100*tickerData[bw["tickerId"]]["option"]["price"]), '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0,
            #                 0,0, 0, 0, 0, 0, 0, 'MA', '01'])

        # if self.change_flag is True:
        #     dataList2 = [
        #         [QCheckBox("AMD"), int(100*tickerData[4100]["underlyer"]["price"]), '063802', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        #     ]
        #     self.change_flag = False
        # elif self.change_flag is False:
        #     dataList2 = [
        #         [QCheckBox("AMD"), int(100*tickerData[4100]["underlyer"]["price"]), '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        #     ]
        #     self.change_flag = True

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
    with open('cc.xml') as fd:
        ccdict = xmltodict.parse(fd.read())

    bars = {}
    endflag = {}

    app = QApplication([])
    # you could process a CSV file to create this data
    header = ['BWSymbol', 'Type', 'Bid', 'Ask', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd']
    # a list of (fname, lname, age, weight) tuples
    checkbox1 = QCheckBox("1");
    checkbox1.setChecked(True)
    dataList = [
        [checkbox1, 0, '058176', '01', 'rb1705,rb1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
        # [QCheckBox("AMD"), 98, '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'MA', '01'],
    ]

    globvars.init_globvars()

    ibapp = IBapi()
    ibapp.connect('127.0.0.1', 7497, 1)

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    mainLogger = logger.initMainLogger()
    initialTickerId = 4100
    tv = []
    itv = []
    tickerData = {}

    mainLogger.info('Started')
    tickerId = initialTickerId
    for bw in ccdict["coveredCalls"]["bw"]:

        dataList.append([QCheckBox(bw["underlyer"]["@tickerSymbol"]), 0, '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 'MA', '01'])
        # dataList.append([QCheckBox(bw["option"]["@tickerSymbol"]), 0, '058176', '02', 'cu1705,cu1710', 0, 0, 0, 0, 0,
        #                 0, 0, 0, 0, 0, 0, 'MA', '01'])

        mainLogger.info("querying no. %s: %s", bw["@id"], bw["underlyer"]["@tickerSymbol"])
        bw["tickerId"] = tickerId


        underlyer = Contract()
        underlyer.symbol = bw["underlyer"]["@tickerSymbol"]
        underlyer.secType = "STK"
        underlyer.exchange = "SMART"
        underlyer.currency = "USD"

        option = Contract()
        option.symbol = bw["underlyer"]["@tickerSymbol"]
        option.secType = "OPT"
        option.exchange = "SMART"
        option.currency = "USD"
        option.lastTradeDateOrContractMonth = bw["option"]["@expiry"]
        option.strike = bw["option"]["@strike"]
        option.right = "Call"
        option.multiplier = "100"

        now = datetime.datetime.now()
        dt = now.strftime("%Y%m%d %H:%M:00")
        dt = now.strftime("%Y%m%d 22:00:00")
        tickerData[bw["tickerId"]] = bw
        tickerData[bw["tickerId"]+1] = bw
        # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
        # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
        #    app.reqHistoricalData(bw["tickerId"], option, dt, "60 S", "10 secs", "MIDPOINT", 1, 1, False, [])
        #    app.reqHistoricalData(bw["tickerId"]+1, underlyer, dt, "60 S", "10 secs", "MIDPOINT", 1, 1, False, [])

        tickerData[bw["tickerId"]]["underlyer"][const.BIDPRICE] = 0
        tickerData[bw["tickerId"]]["underlyer"][const.ASKPRICE] = 0
        tickerData[bw["tickerId"]]["underlyer"][const.LASTPRICE] = 0

        ibapp.reqMktData(bw["tickerId"], underlyer, "", False, False, [])
        ibapp.reqMktData(bw["tickerId"]+1, option, "", False, False, [])
        tv.append(0)
        itv.append(0)
        tickerId += 2



    win = MyWindow(dataList, header)
    win.show()
    # win.table_model.setDataList(dataList)
    # timer = threading.Timer(10, timer_func, (win, dataList2))
    # timer.start()
    app.exec_()
