# coding=utf-8

from PyQt5.QtWidgets import *

from CMainWindow import CMainWindow
from BrkApi import BrkApi
from BrkConnection import BrkConnection

from Account import Account
import logger as logger
from globals import globvars
import const
from covcall import covered_call

from time import time

import time
import xmltodict

from datetime import datetime, time, timedelta
import traceback


def sig_handler ( signum, frame):
    print ("segfault")
    traceback.print_stack(frame)

now = datetime.now()
dt = now.strftime("%Y%m%d 21:59:59")


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
        if 'closed' in bw:
            del bw
            continue
        globvars.cc[str(tickerId)] = covered_call(bw, tickerId)
        globvars.bwl.append(globvars.cc[str(tickerId)])
        globvars.cc[str(tickerId + 1)] = globvars.cc[str(tickerId)]
        tickerId += 2

    for cc in globvars.bwl:
        dataList.append(cc.table_data())

    cmw = CMainWindow(dataList, account)

    cmw.initUI(ccdict)

    cmw.show()

    dtnyse = BrkConnection.find_last_sx_opening_time(const.STOCKEXCHANGE_NYSE)
    ifdtnyse = dtnyse.strftime("%Y%m%d %H:%M:%S")

    dtcboe = BrkConnection.find_last_sx_opening_time(const.STOCKEXCHANGE_CBOE)
    ifdtcboe = dtcboe.strftime("%Y%m%d %H:%M:%S")



    capp.exec_()
