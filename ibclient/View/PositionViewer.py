import sys
from datetime import datetime
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import mplfinance as mpf
from matplotlib.figure import Figure

class SnappingCursor:
    """
    A cross hair cursor that snaps to the data point of a line, which is
    closest to the *x* position of the cursor.

    For simplicity, this assumes that *x* values of the data are sorted.
    """
    def __init__(self, ax, line):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        self.x, self.y = line.get_data()
        self._last_index = None
        # text location in axes coords
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            self._last_index = None
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            index = min(np.searchsorted(self.x, x), len(self.x) - 1)
            if index == self._last_index:
                return  # still on the same data point. Nothing to do.
            self._last_index = index
            x = self.x[index]
            y = self.y[index]
            # update the line positions
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            self.text.set_text('x=%1.2f, y=%1.2f' % (x, y))
            self.ax.figure.canvas.draw()

class PositionViewer(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.sc = FigureCanvasQTAgg(Figure(figsize=(1, 1),tight_layout=True, facecolor='olive', edgecolor='blue'))
        self.ax = self.sc.figure.subplots()
        self.ax.set_facecolor('moccasin')
        self.ax2 = self.ax.twinx()

        # line, = self.ax.plot(x, y, 'o')
        # self.sc.snap_cursor = SnappingCursor(self.ax, line)
        # self.sc.canvas.mpl_connect('motion_notify_event', self.sc.snap_cursor.on_mouse_move)

        daily = pd.read_csv("Misc/Demo/Demo.csv", index_col=0, parse_dates=True)
        daily.drop('Adj Close', axis=1, inplace=True)

        mpf.plot(daily,type='candle', mav=4, ax=self.ax, tight_layout=True,figscale=0.75,show_nontrading=False)

        for label in self.ax.xaxis.get_ticklabels():
            label.set_rotation(0)
        self.ax.axhline()
        self.ax.xaxis_date()
        self.ax.grid(True)
        self.ax.legend(loc=0)
        self.ax2.set_ylabel("STOCK - SPY")
        self.ax.set_ylabel("OPTION - TIMEVALUE")
        qvb = QVBoxLayout()
        qvb.addWidget(self.sc)
        self.setLayout(qvb)

    def updateMplChart(self, cc, alns):
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
        # dfop.is_copy = None
        dfop['date'] = pd.to_datetime(dfop['date'], format=format)

        # dfsk.is_copy = None
        dfsk['date'] = pd.to_datetime(dfsk['date'], format=format)

        dfsk = dfsk.set_index('date')
        dfop = dfop.set_index('date')

        dfsk = dfsk.sort_index()
        dfop = dfop.sort_index()

        comb = dfsk.merge(dfop, how='outer', on=['date'])
        comb.sort_values(by='date', inplace=True)
        comb.columns = ['Open', 'High', 'Low', 'Close', 'OOpen', 'OHigh', 'OLow', 'OClose']

        comb['strike']    = comb.apply(lambda row: self.calc_strike(cc,row), axis=1)
        comb['timevalue'] = comb.apply(lambda row: self.calc_timevalue(cc,row), axis=1)

        if datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y%m%d %H:%M:%S")<comb.iloc[0].name:
            vlinedictlst = [comb.iloc[0].name]
        else:
            vlinedictlst = [datetime.strftime(datetime.strptime(cc.statData.buyWrite["@enteringTime"], "%Y%m%d %H:%M:%S"), "%Y%m%d %H:%M:%S")]

        strikeLine=[]
        prevstrike = 0
        for a in alns:
            if datetime.strptime(a[0], "%Y%m%d %H:%M:%S")<comb.iloc[0].name or datetime.strptime(a[0], "%Y%m%d %H:%M:%S")>comb.iloc[-1].name:
                if datetime.strptime(a[0], "%Y%m%d %H:%M:%S")<comb.iloc[0].name:
                    #outsider left
                    strikeLine.append((comb.iloc[0].name, a[1]))
                    prevstrike = a[1]
                else:
                    #outsider right
                    strikeLine.append((comb.iloc[-1].name, a[1]))
                    prevstrike = a[1]
            else:
                #insider
                strikeLine.append((a[0], prevstrike))
                strikeLine.append((a[0], a[1]))
                prevstrike = a[1]

        if cc.statData.exitingTime != "":
            if pd.to_datetime(cc.statData.exitingTime) > comb.iloc[-1].name:
                strikeLine.append((comb.iloc[-1].name, prevstrike))
            else:
                strikeLine.append((cc.statData.exitingTime, prevstrike))
        else:
            strikeLine.append((comb.iloc[-1].name, prevstrike))

        for ra in cc.statData.rollingActivity:
            rastrptime = datetime.strptime(ra["when"], "%Y%m%d %H:%M:%S")
            if pd.to_datetime(rastrptime) < comb.iloc[0].name or pd.to_datetime(rastrptime) > comb.iloc[-1].name:
                #move outlier into the range
                if pd.to_datetime(rastrptime) < comb.iloc[0].name:
                    rastrptime = comb.iloc[0].name
                else:
                    rastrptime = comb.iloc[-1].name

            vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))
            if pd.to_datetime(rastrptime) < comb.iloc[0].name or pd.to_datetime(rastrptime) > comb.iloc[-1].name:
                #move outlier into the range
                if pd.to_datetime(rastrptime) < comb.iloc[0].name:
                    rastrptime = comb.iloc[0].name
                else:
                    rastrptime = comb.iloc[-1].name
            vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))

            if cc.statData.exitingTime != "":
                rastrptime = cc.statData.exitingTime
                if pd.to_datetime(rastrptime) < comb.iloc[0].name or pd.to_datetime(rastrptime) > comb.iloc[-1].name:
                    #move outlier into the range
                    if pd.to_datetime(rastrptime) < comb.iloc[0].name:
                        rastrptime = comb.iloc[0].name
                    else:
                        rastrptime = comb.iloc[-1].name
                vlinedictlst.append(datetime.strftime(rastrptime, "%Y%m%d %H:%M:%S"))

        apdict = mpf.make_addplot(comb['timevalue'], ax=self.ax, color='black')
        strkdict = mpf.make_addplot(comb['strike'], scatter=True, ax=self.ax2, y_on_right=True, color='green')

        mpf.plot(comb,addplot=apdict, returnfig = True,type='candle', ax=self.ax2,
                 vlines=dict(vlines=vlinedictlst, linewidths=1),
                 alines = dict(alines=strikeLine, colors='r', linewidths=1),
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
