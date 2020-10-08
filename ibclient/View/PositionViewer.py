from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# import pandas as pd
# from scipy.integrate import quad
# import numpy as np
from datetime import datetime

import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf
from matplotlib.figure import Figure

#Different Views and Graphs and Charts concerning a specific position from our portfolio
class PositionViewer(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.setGeometry(70, 150, 1326, 582)

        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1)))
        self.sc_ax = self.sc.figure.subplots()

        qvb = QVBoxLayout()
        qvb.addWidget(self.sc)

        self.setLayout(qvb)

    def calc_timevalue(self, row, strike):
        sval = (row['SHigh'] + row['SLow']) / 2
        oval = (row['OHigh'] + row['OLow']) / 2

        if sval < strike:
            tv = oval
        else:
            tv = oval - (sval - strike)
        return tv

    def updateMplChart(self, cc):

        self.sc_ax.clear()

        dfsk = cc.histData
        dfop = cc.ophistData

        dfsk.columns = ['Date', 'Open', 'High', 'Low', 'Close']
        dfop.columns = ['Date', 'Open', 'High', 'Low', 'Close']

        # dfsk.reset_index(inplace=True)
        # dfsk.index.name = 'Dates'

        # dfop.reset_index(inplace=True)
        # dfop.index.name = 'Dateo'

        dfsk = dfsk.sort_index()
        dfop = dfop.sort_index()

        rsk, csk = dfsk.shape
        rop, cop = dfop.shape

        comb = dfsk.merge(dfop, on=['Date'])
        comb.columns = ['Date', 'SOpen', 'SHigh', 'SLow', 'SClose', 'OOpen', 'OHigh', 'OLow', 'OClose']
        comb['timevalue'] = comb.apply(lambda row: self.calc_timevalue(row, cc.statData.strike), axis=1)

        cols = ['Date', 'Open', 'High', 'Low', 'Close']

        tvcols = ['Date', 'Open']
        self.dailys = dfsk[cols]

        self.tvdailys = dfsk[tvcols]
        self.tvdailys = self.tvdailys -cc.statData.strike

        candlestick_ohlc(self.sc_ax, self.dailys.values, colorup='#77d879', colordown='#db3f3f', width=0.001)
#        candlestick_ohlc(self.sc_ax, dfsk[cols].values, colorup='#77d879', colordown='#db3f3f', width=0.001)

        ax = self.sc_ax.twinx()
        ax.plot(comb['Date'], comb['timevalue'])

        self.sc_ax.axhline(y=cc.statData.strike)

        for label in self.sc_ax.xaxis.get_ticklabels():
            label.set_rotation(45)

        self.sc_ax.xaxis_date()
        self.sc_ax.set_xlabel('time')

        enttime = datetime.strptime(cc.statData.enteringTime, "%Y %b %d %H:%M:%S")
        enttime = mdates.date2num(enttime)
        self.sc_ax.axvline(x=enttime)
        for ra in cc.statData.rollingActivity:
            rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
            ratime = mdates.date2num(rastrptime)
            self.sc_ax.axvline(x=ratime, color='r')

        # timePassed = datetime.now() - beg
        # self.statData.duration = str(timePassed.days)

        self.sc_ax.set_ylabel(cc.statData.buyWrite["underlyer"]["@tickerSymbol"])

        # self.sc_ax2 = self.sc_ax.twinx()
        # self.sc_ax2.set_ylabel('timevalue', color='r')
        # self.sc_ax2.plot(self.tvdailys.values, color='r')

        self.sc_ax.grid(True)
        self.sc_ax.legend(loc=0)

        self.sc.draw()



