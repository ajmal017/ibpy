from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pandas as pd
from scipy.integrate import quad
import numpy as np
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

    def updateMplChart(self, cc):
        self.sc_ax.clear()
        df = cc.histData
        dfop = cc.ophistData

        comb = df.merge(dfop, on=['Date'])
        comb.columns = ['Date', 'SOpen', 'SHigh', 'SLow', 'SClose', 'OOpen', 'OHigh', 'OLow', 'OClose']


        df.reset_index(inplace=True)
        df.index.name = 'Date'
        cols = ['Date', 'Open', 'High', 'Low', 'Close']
        tvcols = ['Date', 'Open']
        self.dailys = df[cols]

        self.tvdailys = df[tvcols]
        self.tvdailys = self.tvdailys -cc.statData.strike

        candlestick_ohlc(self.sc_ax, self.dailys.values, colorup='#77d879', colordown='#db3f3f', width=0.001)
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



