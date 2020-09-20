import xmltodict
from datetime import datetime, time, timedelta
import traceback

from PyQt5.QtWidgets import *

from CMainWindow import CMainWindow
from BrkApi import BrkApi
from Account import Account
import logger as logger
from globals import globvars
from covcall import covered_call


def sig_handler ( signum, frame):
    print ("segfault")
    traceback.print_stack(frame)

now = datetime.now()
dt = now.strftime("%Y%m%d 21:59:59")

if __name__ == '__main__':
    globvars.init_globvars()
    account = Account()
    capp = QApplication([])

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
    capp.exec_()
