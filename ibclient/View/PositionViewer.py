import sys
from datetime import datetime
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import mplfinance as mpf
from matplotlib.figure import Figure

class PositionViewer(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1),tight_layout=True, facecolor='olive', edgecolor='blue'))
        self.ax = self.sc.figure.subplots()
        self.ax.set_facecolor('moccasin')
        self.ax2 = self.ax.twinx()

        daily = pd.read_csv("Misc/Demo/Demo.csv", index_col=0, parse_dates=True)
        daily.drop('Adj Close', axis=1, inplace=True)

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

    def updateMplChart(self, cc):
        self.ax.clear()
        self.ax2.clear()

        dfsk = cc.histData
        dfop = cc.ophistData

        dfsk = dfsk[['open', 'high', 'low', 'close']]
        dfop = dfop[['open', 'high', 'low', 'close']]

        dfsk.reset_index(inplace=True)
        dfop.reset_index(inplace=True)
        dfop.drop('level_0', axis=1, inplace=True)

        #avoid copy warning of pandas as we are aware of this issue:
        pd.set_option('mode.chained_assignment', None)

        format = "%Y-%m-%d  %H:%M:%S"
        dfop.is_copy = None
        dfop['date'] = pd.to_datetime(dfop['date'], format=format)

        dfsk.is_copy = None
        dfsk['date'] = pd.to_datetime(dfsk['date'], format=format)


        dfsk = dfsk.set_index('date')
        dfop = dfop.set_index('date')

        dfsk = dfsk.sort_index()
        dfop = dfop.sort_index()

        comb = dfsk.merge(dfop, on=['date'])
        comb.sort_values(by='date', inplace=True)
        comb.columns = ['Open', 'High', 'Low', 'Close', 'OOpen', 'OHigh', 'OLow', 'OClose']

        comb['strike']    = comb.apply(lambda row: self.calc_strike(cc,row), axis=1)
        comb['timevalue'] = comb.apply(lambda row: self.calc_timevalue(cc,row), axis=1)

        if datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y%m%d %H:%M:%S")<comb.iloc[0].name:
            vlinedictlst = [comb.iloc[0].name]
        else:
            vlinedictlst = [datetime.strftime(datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y%m%d %H:%M:%S"), "%Y%m%d %H:%M:%S")]
        hlinelst = []
        collst=[]
        for ra in cc.statData.rollingActivity:
            rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
            if pd.to_datetime(rastrptime) < comb.iloc[0].name:
                vlinedictlst.append(comb.iloc[0].name)
            else:
                vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))
            hlinelst.append(float(ra["strike"]))
            collst.append('r')

        apdict = mpf.make_addplot(comb['timevalue'], ax=self.ax, color='black')
        strkdict = mpf.make_addplot(comb['strike'], ax=self.ax2, color='green')

        # mpf.plot(comb,addplot=[apdict,strkdict], returnfig = True,type='candle', ax=self.ax2,
        #          vlines=dict(vlines=vlinedictlst, linewidths=1),
        #          tight_layout=True,show_nontrading=False,style='yahoo')

        mpf.plot(comb,addplot=apdict, returnfig = True,type='candle', ax=self.ax2,
                 vlines=dict(vlines=vlinedictlst, linewidths=1),
                 tight_layout=True,show_nontrading=False,style='yahoo')

        for label in self.ax.xaxis.get_ticklabels():
            label.set_rotation(0)

        # self.ax.xaxis_date()
        # self.ax.set_xlabel('time')
        self.ax2.set_ylabel(cc.statData.buyWrite["underlyer"]["@tickerSymbol"])
        # self.ax2.tick_params(axis='y', labelcolor='b')
        self.ax.set_ylabel("TIMEVALUE")
        self.ax.grid(True)
        # self.ax.legend(loc=0)
        self.sc.draw()
        return True

    def numpy2Datetime(self, input):
        #input is of type numpy.datetime64, e.g. "numpy.datetime64('2020-08-07T15:30:00.000000000')"
        dt64 = input
        ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.utcfromtimestamp(ts)

    def calc_strike(self, cc, row):
        if len(cc.statData.rollingActivity) == 0:
            return cc.statData.buyWrite["option"]["@strike"]
        else:
            entrydatetime = datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y%m%d %H:%M:%S")
            radatetime = datetime.strptime(cc.statData.rollingActivity[0]["when"], "%Y%m%d %H:%M:%S")

            if self.numpy2Datetime(row.name) < entrydatetime:
                return np.nan
            elif self.numpy2Datetime(row.name) < radatetime:
                return cc.statData.buyWrite["option"]["@strike"]
            else:
                for i, ra in enumerate(cc.statData.rollingActivity):
                    radatetime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
                    if self.numpy2Datetime(row.name) < radatetime:
                        return ra["strike"]

            return ra["strike"]

    def calc_timevalue(self, cc, row):
        entrydatetime = datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y%m%d %H:%M:%S")

        if self.numpy2Datetime(row.name) < entrydatetime:
            return np.nan

        sval = (row['High'] + row['Low']) / 2
        oval = (row['OHigh'] + row['OLow']) / 2
        oval = row['OClose']

        if sval < float(row["strike"]):
            tv = oval
        else:
            tv = oval - (sval - float(row["strike"]))
        return tv
