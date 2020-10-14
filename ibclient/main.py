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

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    raise OSError("Couldn't open device!")

signal.signal(signal.SIGSEGV, handler)

SIZES = ["secs", "min", "mins", "hour", "hours", "day", "week", "month"]
DURATIONS = ["S", "D", "W", "M", "Y"]

def _validate(value: str, name: str, valid: List[str]) -> None:
    tokens = value.split()
    if len(tokens) != 2:
        raise ValidationException("{name} should be in the form <digit> <{name}>")
    _validate_in(tokens[1], name, valid)
    try:
        int(tokens[0])
    except ValueError as ve:
        raise ValidationException(f"{name} dimenion not a valid number: {ve}")

class ValidationException(Exception):
    pass

def _validate_in(value: str, name: str, valid: List[str]) -> None:
    if value not in valid:
        raise ValidationException(f"{value} not a valid {name} unit: {','.join(valid)}")

def validate_duration(duration: str) -> None:
    _validate(duration, "duration", DURATIONS)


def validate_size(size: str) -> None:
    _validate(size, "size", SIZES)


def validate_data_type(data_type: str) -> None:
    _validate_in(
        data_type,
        "data_type",
        [
            "TRADES",
            "MIDPOINT",
            "BID",
            "ASK",
            "BID_ASK",
            "ADJUSTED_LAST",
            "HISTORICAL_VOLATILITY",
            "OPTION_IMPLIED_VOLATILITY",
            "REBATE_RATE",
            "FEE_RATE",
            "YIELD_BID",
            "YIELD_ASK",
            "YIELD_BID_ASK",
            "YIELD_LAST",
        ],
    )


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

    # argp = argparse.ArgumentParser()
    # argp.add_argument("symbol", nargs="+")
    # argp.add_argument(
    #     "-d", "--debug", action="store_true", help="turn on debug logging"
    # )
    # argp.add_argument(
    #     "-p", "--port", type=int, default=4002, help="local port for TWS connection"
    # )
    # argp.add_argument("--size", type=str, default="1 min", help="bar size")
    # argp.add_argument("--duration", type=str, default="1 D", help="bar duration")
    # argp.add_argument(
    #     "-t", "--data-type", type=str, default="MIDPOINT", help="bar data type"
    # )
    # argp.add_argument(
    #     "--base-directory",
    #     type=str,
    #     default="data",
    #     help="base directory to write bar files",
    # )
    # argp.add_argument(
    #     "--currency", type=str, default="USD", help="currency for symbols"
    # )
    # argp.add_argument(
    #     "--exchange", type=str, default="SMART", help="exchange for symbols"
    # )
    # argp.add_argument(
    #     "--expiry", type=str, default="", help="expiry for options"
    # )
    #
    # argp.add_argument(
    #     "--strike", type=str, default="", help="strike for options"
    # )
    #
    # argp.add_argument(
    #     "--security-type", type=str, default="OPT", help="security type for symbols"
    # )
    # argp.add_argument(
    #     "--start-date",
    #     help="First day for bars",
    #     default=now - timedelta(days=2),
    #     action=DateAction,
    # )
    # argp.add_argument(
    #     "--end-date", help="Last day for bars", default=now, action=DateAction,
    # )
    # argp.add_argument(
    #     "--max-days", help="Set start date to earliest date", action="store_true",
    # )
    # args = argp.parse_args()

    # try:
    #     validate_duration(args.duration)
    #     validate_size(args.size)
    #     args.data_type = args.data_type.upper()
    #     validate_data_type(args.data_type)
    # except ValidationException as ve:
    #     print(ve)
    #     sys.exit(1)


    globvars.init_globvars()
    capp = QApplication([])

    mainLogger = logger.initMainLogger()
    globvars.set_logger(mainLogger)

    model = CMTModel()
    controller = Controller(model)
    model.initData(controller)

    view = CMTWidget(model)
    cmw = CMainWindow(view, controller, mainLogger)
    controller.initData(view)

    cmw.initUI()
    cmw.show()
    controller.resetAllColumns()
    capp.exec_()
