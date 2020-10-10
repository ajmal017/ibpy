from datetime import datetime
import pandas as pd
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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

        # daily = pd.read_csv("Misc/Demo/SPY_20110701_20120630_Bollinger.csv", index_col=0, parse_dates=True)
        daily = pd.read_csv("Misc/Demo/Demo.csv", index_col=0, parse_dates=True)

        daily.drop('Adj Close', axis=1, inplace=True)

#        mpf.plot(daily,type='candle', mav=4, ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=False, style="yahoo")
        mpf.plot(daily,type='candle', mav=4, ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=False)

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

    def numpy2Datetime(self, input):
        #input is of type numpy.datetime64, e.g. "numpy.datetime64('2020-08-07T15:30:00.000000000')"
        dt64 = input
        ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.utcfromtimestamp(ts)

    def calc_strike(self, cc, row):
        radatetime = datetime.strptime(cc.statData.rollingActivity[0]["when"], "%Y%m%d %H:%M:%S")
        if self.numpy2Datetime(row.name) < radatetime:
            # this is cc.statData.buyWrite["option"]["@strike"]
            return 150
        else:
            for i, ra in enumerate(cc.statData.rollingActivity):
                radatetime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
                if self.numpy2Datetime(row.name) < radatetime:
                    return ra["strike"]

        return ra["strike"]

    def calc_timevalue(self, row):
        sval = (row['High'] + row['Low']) / 2
        oval = (row['OHigh'] + row['OLow']) / 2

        if sval < float(row["strike"]):
            tv = oval
        else:
            tv = oval - (sval - float(row["strike"]))
        return tv

    def updateMplChart(self, cc):
        self.ax.clear()
        self.ax2.clear()

        dfsk = cc.histData
        dfop = cc.ophistData

        dfskorg = dfsk
        dfoporg = dfop

        format = "%Y%m%d  %H:%M:%S"
        dfop['Datetime'] = pd.to_datetime(dfop['Datetime'], format=format)
        dfsk['Datetime'] = pd.to_datetime(dfsk['Datetime'], format=format)

        dfsk = dfsk.set_index('Datetime')
        dfop = dfop.set_index('Datetime')

        dfsk = dfsk.sort_index()
        dfop = dfop.sort_index()

        rsk, csk = dfsk.shape
        rop, cop = dfop.shape

        comb = dfsk.merge(dfsk, on=['Datetime'])
        comb.sort_values(by='Datetime', inplace=True)
        comb.columns = ['Open', 'High', 'Low', 'Close', 'OOpen', 'OHigh', 'OLow', 'OClose']

        comb['strike']    = comb.apply(lambda row: self.calc_strike(cc,row), axis=1)
        comb['timevalue'] = comb.apply(lambda row: self.calc_timevalue(row), axis=1)

        vlinedictlst = [datetime.strftime(datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y %b %d %H:%M:%S"), "%Y%m%d %H:%M:%S")]
        hlinelst = []
        collst=[]
        for ra in cc.statData.rollingActivity:
            rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
            vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))
            hlinelst.append(float(ra["strike"]))
            collst.append('r')

        apdict = mpf.make_addplot(comb['timevalue'], ax=self.ax2, color='black')

        mpf.plot(comb,addplot=apdict, returnfig = True,type='candle', ax=self.ax,
                 hlines=dict(hlines=hlinelst, linewidths=1,colors=collst,linestyle='-.'),
                 vlines=dict(vlines=vlinedictlst, linewidths=1),
                 tight_layout=True,figscale=0.75,show_nontrading=False,style='yahoo')

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
        #mpf.plot(dfsk,type='candle', mav=4, ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=False, style="yahoo")
#        mpf.plot(dfsk,type='candle', ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=False)

#        self.ax.axhline(y=cc.statData.strike)

        # self.ax2.plot(comb['Date'], comb['timevalue'])

        # for label in self.ax.xaxis.get_ticklabels():
        #     label.set_rotation(0)
        #
        # self.ax.xaxis_date()
        # self.ax.set_xlabel('time')
        #
        # enttime = datetime.strptime(cc.statData.enteringTime, "%Y %b %d %H:%M:%S")
        # enttime = mdates.date2num(enttime)
        # self.ax.axvline(x=enttime)
        # for ra in cc.statData.rollingActivity:
        #     rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
        #     ratime = mdates.date2num(rastrptime)
        #     self.ax.axvline(x=ratime, color='r')

        self.ax.set_ylabel(cc.statData.buyWrite["underlyer"]["@tickerSymbol"])

        self.ax.grid(True)
        self.ax.legend(loc=0)

        self.sc.draw()

        return True



