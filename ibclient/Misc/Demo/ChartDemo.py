import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from Logs import logger as logger
from Misc.globals import globvars

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf
from matplotlib.figure import Figure

def calc_timevalue(row, strike):
    sval = (row['SHigh'] + row['SLow'])/2
    oval = (row['OHigh'] + row['OLow'])/2

    if sval < strike:
        tv = oval
    else:
        tv = oval - (sval-strike)
    return tv

def prepareYahooDemo():
    ret = pd.read_csv("../../Misc/Demo/yahoofinance-INTC-19950101-20040412.csv", index_col=0,
                          parse_dates=True)
    ret.drop('Adj Close', axis=1, inplace=True)
    ret.reset_index(inplace=True)
    ret.index.name = 'Date'
    ret["Date"] = mdates.date2num(ret["Date"].values)
    cols = ['Date', 'Open', 'High', 'Low', 'Close']
    ret = ret[cols]
    return ret


globvars.init_globvars()
logger = logger.initMainLogger()

class CMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chart Demo')
        self.setGeometry(100, 200, 1500, 500)

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()

        sdatadf = prepareYahooDemo()

        # sdatadf = pd.read_csv("../../Model/Cache/RGEN.csv", index_col=0)
        # odtaadf = pd.read_csv("../../Model/Cache/RGEN20201120.csv", index_col=0)
        # cols = ['Date', 'Open', 'High', 'Low', 'Close']
        # sdatadf.columns = cols
        # odtaadf.columns = cols

        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1)))
        self.ax = self.sc.figure.subplots()
        self.ax.axhline()
        self.ax.xaxis_date()
        self.ax.grid(True)
        self.ax.legend(loc=0)
        cols = ['Date', 'Open', 'High', 'Low', 'Close']

        candlestick_ohlc(self.ax, sdatadf[cols].values, colorup='#77d879', colordown='#db3f3f', width=0.001)

        qvb = QVBoxLayout()
        qvb.addWidget(self.sc)

        self.setLayout(qvb)

if __name__ == '__main__':
    capp = QApplication([])
    demoWindow = DemoWindow()
    # demoWindow.show()

    mainWindow = CMainWindow()
    mainWindow.setCentralWidget(demoWindow)
    mainWindow.show()

    capp.exec_()
