from datetime import datetime
import pandas as pd
import numpy as np

from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from Logs import logger as logger
from Misc.globals import globvars

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
#from mplfinance.original_flavor import candlestick_ohlc
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
    # ret.reset_index(inplace=True)
    ret.index.name = 'Date'
    #ret["Date"] = mdates.date2num(ret["Date"].values)
#    cols = ['Date', 'Open', 'High', 'Low', 'Close']
#    ret = ret[cols]
    return ret

def prepareYahooOpDemo():
    ret = pd.read_csv("../../Misc/Demo/yahoofinance-INTC-19950101-20040412.csv", index_col=0,
                          parse_dates=True)
    ret.drop('Adj Close', axis=1, inplace=True)
    # ret.reset_index(inplace=True)
    ret.index.name = 'Date'
    # ret = ret - 5
    #ret["Date"] = mdates.date2num(ret["Date"].values)
#    cols = ['Date', 'Open', 'High', 'Low', 'Close']
#    ret = ret[cols]
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
        odatadf = prepareYahooOpDemo()

        rgensdatadf = pd.read_csv("../../Model/Cache/RGEN.csv", index_col=0)
        rgenodtaadf = pd.read_csv("../../Model/Cache/RGEN20201120.csv", index_col=0)

        rgensdatadf['Date'] = [ datetime.strftime(mdates.num2date(x), format="%Y%m%d %H:%M:%S") for x in rgensdatadf['Date'] ]
        rgenodtaadf['Date'] = [ datetime.strftime(mdates.num2date(x), format="%Y%m%d %H:%M:%S") for x in rgenodtaadf['Date'] ]

        format = "%Y%m%d  %H:%M:%S"
        rgensdatadf['Date'] = pd.to_datetime(rgensdatadf['Date'], format=format)
        rgenodtaadf['Date'] = pd.to_datetime(rgenodtaadf['Date'], format=format)

        rgensdatadf.set_index('Date', inplace=True)
        rgenodtaadf.set_index('Date', inplace=True)

        rgensdatadf.sort_index(inplace=True)
        rgenodtaadf.sort_index(inplace=True)

        a = {'import': 'trade', 1: 7.8}

        self.rollingActivity = [
            {
                "when" : "20200917 16:15:19",
                "from" : "20200918",
                "to"   : "20201016",
                "strike": "150"
            },
            {
                "when"  : "20201006 20:52:55",
                "from"  : "20201016",
                "to"    : "20201120",
                "strike": "155"
            },
            {
                "when"  : "20201007 20:32:32",
                "from"  : "20201120",
                "to"    : "20201120",
                "strike": "160"
            },
        ]
        # cols = ['Date', 'Open', 'High', 'Low', 'Close']
        # sdatadf.columns = cols
        # odtaadf.columns = cols

        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1)))
        self.ax = self.sc.figure.subplots()
        self.ax.axhline()
        self.ax.xaxis_date()
        self.ax.grid(True)
        self.ax.legend(loc=0)
        self.ax2 = self.ax.twinx()

        comb = rgensdatadf.merge(rgenodtaadf, on=['Date'])
        comb.sort_values(by='Date', inplace=True)
        comb.columns = ['Open', 'High', 'Low', 'Close', 'OOpen', 'OHigh', 'OLow', 'OClose']

        # for ra in rollingActivity:
        #     rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
        #     #ratime = mdates.date2num(rastrptime)
        #     vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))


        comb['strike']    = comb.apply(lambda row: self.calc_strike(row), axis=1)
        comb['timevalue'] = comb.apply(lambda row: self.calc_timevalue(row), axis=1)

        vlinedictlst = []
        hlinelst = []
        for ra in self.rollingActivity:
            rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
            # ratime = mdates.date2num(rastrptime)
            vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))
            hlinelst.append(float(ra["strike"]))

        apdict = mpf.make_addplot(comb['timevalue'], ax=self.ax2, color='black')
        mpf.plot(comb,addplot=apdict, returnfig = True,type='candle', ax=self.ax,
                 hlines=dict(hlines=hlinelst, linewidths=1),
                 vlines=dict(vlines=vlinedictlst, linewidths=1),
                 tight_layout=True,figscale=0.75,show_nontrading=False,style='yahoo')

        qvb = QVBoxLayout()
        qvb.addWidget(self.sc)

        self.setLayout(qvb)


        #self.ax2.set_ylabel("OPTION - TIMEVALUE")
        #cols = ['Date', 'Open', 'High', 'Low', 'Close']

        #df = sdatadf.loc['1995-01-03':'1996-08-20', :]

        #dates_df = pd.DataFrame(sdatadf.index)
        #where_values = pd.notnull(dates_df[(dates_df >= '1996-08-20') & (dates_df <= '1996-08-21')])['Date'].values


        # fig = mpf.plot(rgensdatadf, returnfig = True,type='candle', ax=self.ax,
        #          hlines=[6,7],
        #          vlines=dict(vlines=['1995-07-06', '1996-01-15'],linewidths=(1,2,3),colors=('r','g','b')),
        #          # vlines=dict(vlines='1995-08-06',linewidths=100, alpha=0.4),
        #          tight_layout=True,figscale=0.75,show_nontrading=False,style='yahoo')


        # mpf.plot(odatadf,type='ohlc', mav=4, ax=self.ax2, tight_layout=True,figscale=0.75,show_nontrading=False ,
        #          # fill_between=dict(y1=7,y2=8,where=where_values,alpha=0.5,color='g')
        #          )

        #candlestick_ohlc(self.ax, sdatadf[cols].values, colorup='#77d879', colordown='#db3f3f', width=0.001)
        # x = sdatadf['Date']
        # y = sdatadf['Close']
        # self.ax.plot(self.ax, x, y)

    def numpy2Datetime(self, input):
        #input is of type numpy.datetime64, e.g. "numpy.datetime64('2020-08-07T15:30:00.000000000')"
        dt64 = input
        ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.utcfromtimestamp(ts)

    def calc_strike(self, row):
        radatetime = datetime.strptime(self.rollingActivity[0]["when"], "%Y%m%d %H:%M:%S")
        if self.numpy2Datetime(row.name) < radatetime:
            #this is cc.statData.buyWrite["option"]["@strike"]
            return 150
        else:
            for i,ra in enumerate(self.rollingActivity):
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

if __name__ == '__main__':
    capp = QApplication([])
    demoWindow = DemoWindow()
    # demoWindow.show()

    mainWindow = CMainWindow()
    mainWindow.setCentralWidget(demoWindow)
    mainWindow.show()

    capp.exec_()
