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
import const
from covcall import covered_call

from time import time
import threading
import time
import xmltodict



from datetime import datetime, time, timedelta

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def run_loop():
    globvars.ibapp.run()

if __name__ == '__main__':
    globvars.init_globvars()
    capp = QApplication([])
    globvars.ibapp = BrkApi()

    mainLogger = logger.initMainLogger()
    globvars.set_logger(mainLogger)

    initialtickerId = 4100

    mainLogger.info('Started')
    tickerId = initialtickerId

    globvars.bwl = []

    with open('cc.xml') as fd:
        ccdict = xmltodict.parse(fd.read())

    dataList = [[''       , ''        , ''   , ''      , ''      , ''      , ''       , ''        , ''       , ''       , ''           , ''     , ''      , ''      , ''      , ''      , '0'  , '0'    , '0'  , '0'    , '0'     ]]

    for bw in ccdict["coveredCalls"]["bw"]:
        globvars.cc[str(tickerId)] = covered_call(bw, tickerId)
        globvars.bwl.append(globvars.cc[str(tickerId)])
        globvars.cc[str(tickerId + 1)] = globvars.cc[str(tickerId)]
        tickerId += 2

    globvars.ibapp.connect('127.0.0.1', const.IBPORT, const.IBCLIENTID)
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    globvars.ibapp.reqAccountUpdates(True, "U806698")

    for cc in globvars.bwl:
        dataList.append(cc.table_data())

        mainLogger.info("querying no. %s: %s", bw["@id"], bw["underlyer"]["@tickerSymbol"])

        nyseIsOpen = is_time_between(time(10, 00), time(22, 00))
        cboeIsOpen = is_time_between(time(15, 30), time(22, 00))

        globvars.ibapp.reqContractDetails(cc.ticker_id(), cc.underlyer())

        if nyseIsOpen:
            globvars.ibapp.reqMktData(cc.ticker_id(), cc.underlyer(), "", False, False, [])
        else:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
            now = datetime.now() - timedelta(days=1)
            dt = now.strftime("%Y%m%d 21:50:00")
            globvars.ibapp.reqHistoricalData(cc.ticker_id(), cc.underlyer(), dt, "3600 S", "5 mins", "MIDPOINT", 1, 1, False, [])

        if cboeIsOpen:
            globvars.ibapp.reqMktData(cc.ticker_id()+1   , cc.option(), "", False, False, [])
        else:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
            now = datetime.now() - timedelta(days=1)
            dt = now.strftime("%Y%m%d 21:59:00")
            globvars.ibapp.reqHistoricalData(cc.ticker_id()+1, cc.option(), dt, "3600 S", "5 mins", "MIDPOINT", 1, 1, False, [])

    cmw = CMainWindow(dataList)

    cmw.initUI(ccdict)

    cmw.show()

    capp.exec_()
