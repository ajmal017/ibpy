''' pqt_tableview3.py
explore PyQT's QTableView Model
using QAbstractTableModel to present tabular data
allow table sorting by clicking on the header title
used the Anaconda package (comes with PyQt4) on OS X
(dns)
'''

# coding=utf-8

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

from CMainWindow import CMainWindow
from BrkApi import BrkApi
import logger as logger
from globals import globvars
from covcall import covered_call

from time import time
import threading
import time
import xmltodict
from globals import globvars
import const

from datetime import datetime, time, timedelta

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def timer_func(win, mylist):
    print(">>> timer_func()")
    win.table_model.setDataList(mylist)
    win.table_view.repaint()
    win.table_view.update()

def run_loop():
    ibapp.run()

if __name__ == '__main__':
    capp = QApplication([])
    ibapp = BrkApi()

    globvars.init_globvars()
    mainLogger = logger.initMainLogger()

    initialtickerId = 4100

    mainLogger.info('Started')
    tickerId = initialtickerId

    ibapp.connect('127.0.0.1', const.IBPORT, const.IBCLIENTID)

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    tv = []
    itv = []
    with open('cc.xml') as fd:
        ccdict = xmltodict.parse(fd.read())
    # you could process a CSV file to create this data
    header = ['Symbol', 'Pos', 'Strike', 'Expiry', 'Days', 'Initial', 'UL-Init', 'UL-Last', 'UL-Chge', 'UL-Chge pct','UL-Bid', 'UL-Ask', 'OP-Lst', 'OP-Bid', 'OP-Ask', 'ITV', 'CurTV', 'CurTV/$', 'TV-Chg']
    # a list of (fname, lname, age, weight) tuples
    checkbox1 = QCheckBox("1");
    checkbox1.setChecked(True)
    dataList = [
        [checkbox1, '', '','' '', '', '', '', '0', '0', '0', '0', '0', '0', 0, 0, 0, 0, 0]
    ]
    for bw in ccdict["coveredCalls"]["bw"]:

        (underlyer,option) = covered_call.get_contracts(bw)

        bw["cc"] = covered_call("Call", underlyer, bw["option"]["@strike"], bw["option"]["@expiry"])
        bw["itv"] = bw["cc"].calc_itv(bw)
        bw["ctv"] = bw["cc"].getTimevalue()
        bw["tvprof"] = bw["itv"] - bw["ctv"]
        bw["pac"] = ""

        if (float(bw["option"]["@strike"]) > float(bw["underlyer"]["@price"])):
            ioa = "OTM"
        elif (float(bw["option"]["@strike"]) < float(bw["underlyer"]["@price"])):
            ioa = "ITM"
        else:
            ioa = "ATM"

        bw["ioa_initial"] = ioa

        ioanow = ioa

        dataList.append([QCheckBox(bw["underlyer"]["@tickerSymbol"]), bw["option"]["@strike"], bw["option"]["@expiry"], bw["ioa_initial"],ioanow, 0, 0, 0, 0, 0, 0, bw["itv"], bw["ctv"], bw["tvprof"], bw["pac"]])

        mainLogger.info("querying no. %s: %s", bw["@id"], bw["underlyer"]["@tickerSymbol"])

        bw["tickerId"] = str(tickerId)
        bw["underlyer"]["tickerId"] = str(tickerId)
        bw["option"]["tickerId"] = str(tickerId+1)

        globvars.tickerData[bw["underlyer"]["tickerId"]] = {}
        globvars.tickerData[bw["option"]["tickerId"]] = {}

        globvars.tickerData[bw["underlyer"]["tickerId"]]["bw"] = bw
        globvars.tickerData[bw["option"]["tickerId"]]["bw"] = bw

        globvars.tickerData[bw["underlyer"]["tickerId"]][const.BIDPRICE] = 0
        globvars.tickerData[bw["underlyer"]["tickerId"]][const.ASKPRICE] = 0
        globvars.tickerData[bw["underlyer"]["tickerId"]][const.LASTPRICE] = 0

        globvars.tickerData[bw["option"]["tickerId"]][const.ASKPRICE] = 0
        globvars.tickerData[bw["option"]["tickerId"]][const.LASTPRICE] = 0
        globvars.tickerData[bw["option"]["tickerId"]][const.BIDPRICE] = 0

        nyseIsOpen = is_time_between(time(15, 30), time(22, 00))

        if nyseIsOpen:
            ibapp.reqMktData(bw["underlyer"]["tickerId"], underlyer, "", False, False, [])
            ibapp.reqMktData(bw["option"]["tickerId"]   , option, "", False, False, [])
        else:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
            now = datetime.now() - timedelta(days=1)
            dt = now.strftime("%Y%m%d 21:50:00")
            ibapp.reqHistoricalData(bw["option"]["tickerId"], option, dt, "3600 S", "5 mins", "MIDPOINT", 1, 1, False, [])
            ibapp.reqHistoricalData(bw["underlyer"]["tickerId"], underlyer, dt, "3600 S", "5 mins", "MIDPOINT", 1, 1, False, [])

        tickerId += 2


    cmw = CMainWindow(dataList, header, ccdict)

    # win = MyWindow(dataList, header)
    # win.show()

    capp.exec_()
