from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pandas as pd
from scipy.integrate import quad
import numpy as np
from datetime import datetime

import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import mplfinance as mpf
from matplotlib.figure import Figure

#Different Views and Graphs and Charts concerning a specific position from our portfolio
class PositionViewer(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1),tight_layout=True, facecolor='olive', edgecolor='blue'))
#        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1)))
        self.ax = self.sc.figure.subplots()
        self.ax.set_facecolor('moccasin')
        self.ax2 = self.ax.twinx()

        daily = pd.read_csv("Misc/Demo/SPY_20110701_20120630_Bollinger.csv", index_col=0, parse_dates=True)
        daily.drop('Adj Close', axis=1, inplace=True)

        mpf.plot(daily,type='candle', ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=True)

        for label in self.ax.xaxis.get_ticklabels():
            label.set_rotation(0)
        self.ax.axhline()
        self.ax.xaxis_date()
        self.ax.grid(True)
        self.ax.legend(loc=0)
        self.ax.set_ylabel("STOCK - SPY")
        self.ax2.set_ylabel("OPTION - TIMEVALUE")
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
        self.ax.clear()
        self.ax2.clear()

        dfsk = cc.histData
        dfop = cc.ophistData

        dfskorg = dfsk
        dfoporg = dfop

        idf = pd.read_csv('Misc/Demo/SPY_20110701_20120630_Bollinger.csv', index_col=0, parse_dates=True)

        # dfsk.reset_index(inplace=True)
        # dfsk.index.name = 'Date'

        format = "%Y%m%d  %H:%M:%S"
        dfop['Datetime'] = pd.to_datetime(dfop['Datetime'], format=format)
        dfsk['Datetime'] = pd.to_datetime(dfop['Datetime'], format=format)

        dfsk = dfsk.set_index('Datetime')
        dfop = dfop.set_index('Datetime')

        dfsk = dfsk.sort_index()
        dfop = dfop.sort_index()

        rsk, csk = dfsk.shape
        rop, cop = dfop.shape

        # comb = dfskorg.merge(dfoporg, on=['Date'])
        # comb.sort_values(by='Date', inplace=True)
        # comb.columns = ['Date', 'SOpen', 'SHigh', 'SLow', 'SClose', 'OOpen', 'OHigh', 'OLow', 'OClose']
        # comb['timevalue'] = comb.apply(lambda row: self.calc_timevalue(row, cc.statData.strike), axis=1)

        # cols = ['Date', 'Open', 'High', 'Low', 'Close']
        # tvcols = ['Date', 'Open']
        # self.dailys = dfsk[cols]
        #
        # self.tvdailys = dfsk[tvcols]
        # self.tvdailys = self.tvdailys -cc.statData.strike

        # candlestick_ohlc(self.ax, self.dailys.values, colorup='#77d879', colordown='#db3f3f', width=0.001)
        mpf.plot(dfsk,type='candle', ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=False)

        self.ax.axhline(y=cc.statData.strike)

        # self.ax2.plot(comb['Date'], comb['timevalue'])

        for label in self.ax.xaxis.get_ticklabels():
            label.set_rotation(0)

        self.ax.xaxis_date()
        self.ax.set_xlabel('time')

        enttime = datetime.strptime(cc.statData.enteringTime, "%Y %b %d %H:%M:%S")
        enttime = mdates.date2num(enttime)
        self.ax.axvline(x=enttime)
        for ra in cc.statData.rollingActivity:
            rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
            ratime = mdates.date2num(rastrptime)
            self.ax.axvline(x=ratime, color='r')

        self.ax.set_ylabel(cc.statData.buyWrite["underlyer"]["@tickerSymbol"])

        self.ax.grid(True)
        self.ax.legend(loc=0)

        self.sc.draw()

        return True



