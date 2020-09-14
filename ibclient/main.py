# coding=utf-8

from PyQt5.QtWidgets import *

from CMainWindow import CMainWindow
from BrkApi import BrkApi
from Account import Account
import logger as logger
from globals import globvars
import const
from covcall import covered_call

from time import time
import threading
import time
import xmltodict

from datetime import datetime, time, timedelta
import traceback


def sig_handler ( signum, frame):
    print ("segfault")
    traceback.print_stack(frame)


def find_last_sx_opening_time(which_stockexchange: int):
    today = datetime.today()
    tod = datetime.now().time()
    weekday = datetime.weekday(today) # 6=sunday, 0=monday

    if which_stockexchange == const.STOCKEXCHANGE_NYSE:
        opening_hour = time(10,00,00,00)
        closing_hour = time(2,00,00,00)
    else:
        closing_hour = time(21,59,59,59)
        opening_hour = time(15,30,00,00)

    if weekday == 0: #monday
        if tod < opening_hour:  #monday morning
            return datetime.combine(today-timedelta(2), closing_hour)
        if tod > closing_hour: #monday night
            return datetime.combine(today, closing_hour)

    if weekday >= 1 or weekday <= 4:
        if tod < opening_hour: #tuesday to friday morning
            return datetime.combine(today, closing_hour)
        if tod > closing_hour: #tuesday to friday night
            return datetime.combine(today, closing_hour)

    if weekday == 5: #saturday
        return datetime.combine(today, closing_hour)

    if weekday == 6: #sunday
        return datetime.combine(today-timedelta(1), closing_hour)

now = datetime.now()
dt = now.strftime("%Y%m%d 21:59:59")


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
    account = Account()

    globvars.ibapp = BrkApi(account)

    mainLogger = logger.initMainLogger()
    globvars.set_logger(mainLogger)

    globvars.logger.info("**********************************************")
    globvars.logger.info("*          IBPY - Covered Call Analyzer      *")
    globvars.logger.info("**********************************************")

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

    for cc in globvars.bwl:
        dataList.append(cc.table_data())


    cmw = CMainWindow(dataList, account)

    cmw.initUI(ccdict)

    cmw.show()

    globvars.ibapp.connect('127.0.0.1', const.IBPORT, const.IBCLIENTID)
    api_thread = threading.Thread(target=run_loop, daemon=True)

    globvars.ibapp.reqAccountUpdates(True, "U806698")

    for cc in globvars.bwl:
        # dataList.append(cc.table_data())

        mainLogger.info("querying no. %s: %s", bw["@id"], bw["underlyer"]["@tickerSymbol"])

        nyseIsOpen = is_time_between(time(10, 00), time(22, 00)) and datetime.today().weekday() > 0 and datetime.today().weekday() < 5
        cboeIsOpen = is_time_between(time(15, 30), time(22, 00)) and datetime.today().weekday() > 0 and datetime.today().weekday() < 5

        #globvars.ibapp.reqContractDetails(cc.ticker_id(), cc.underlyer())

        if nyseIsOpen:
            globvars.ibapp.reqMktData(cc.ticker_id(), cc.underlyer(), "", False, False, [])
        else:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month

            dt = find_last_sx_opening_time(const.STOCKEXCHANGE_NYSE)
            ifdt = dt.strftime("%Y%m%d %H:%M:%S")

            globvars.ibapp.reqHistoricalData(cc.ticker_id(), cc.underlyer(), ifdt, "3600 S", "5 mins", "TRADES", const.HISTDATA_OUTSIDERTH, 1, False, [])

        if cboeIsOpen:
            globvars.ibapp.reqMktData(cc.ticker_id()+1   , cc.option(), "", False, False, [])
            #globvars.ibapp.reqHistoricalData(cc.ticker_id()+1, cc.option(), dt, "2 D", "1 day", "MIDPOINT", 1, 1, False, [])
        else:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month

            dt = find_last_sx_opening_time(const.STOCKEXCHANGE_CBOE)
            ifdt = dt.strftime("%Y%m%d %H:%M:%S")

            globvars.ibapp.reqHistoricalData(cc.ticker_id()+1, cc.option(), ifdt, "1 D", "1 hour", "MIDPOINT", 1, 1, False, [])

    api_thread.start()

    capp.exec_()
