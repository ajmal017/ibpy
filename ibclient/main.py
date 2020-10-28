import signal, os
import sys
import time
import argparse
from datetime import datetime, timedelta
from dateutil.parser import parse

import faulthandler; faulthandler.enable()
from typing import List, Optional

from PyQt5.QtWidgets import *

from View.CMainWindow import CMainWindow
from View.CMTWidget import CMTWidget
from Controller.CMTController import  Controller
from Model.CMTModel import CMTModel
from Logs import logger as logger
from Misc.globals import globvars
from Model.resamplecsv import resample

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    raise OSError("Couldn't open device!")

signal.signal(signal.SIGSEGV, handler)

if __name__ == '__main__':
    now = datetime.now()

    class DateAction(argparse.Action):
        """Parses date strings."""

        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            value: str,
            option_string: str = None,
        ):
            """Parse the date."""
            setattr(namespace, self.dest, parse(value))



    globvars.init_globvars()
    capp = QApplication([])


    mainLogger = logger.initMainLogger()
    globvars.set_logger(mainLogger)


    model = CMTModel()
    controller = Controller(model)
    model.initData(controller)

    view = CMTWidget(model, controller)
    cmw = CMainWindow(view, controller, mainLogger)
    controller.initData(view)

    resample(False, "ALL")

    cmw.initUI()
    cmw.show()
    controller.resetAllColumns()
    capp.exec_()
