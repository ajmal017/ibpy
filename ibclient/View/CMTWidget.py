import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pandas as pd
import matplotlib.dates as mdates
from scipy.integrate import quad
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from mplfinance.original_flavor import candlestick_ohlc


# from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates

from matplotlib.figure import Figure

import numpy as np

from Model.CMTModel import CMTModel, PrxyModel
from Controller.covcall import covered_call
import Misc.const

## Helper functions ##
def dN(x):
    ''' Probability density function of standard normal random variable x.'''
    return math.exp(-0.5 * x ** 2) / math.sqrt(2 * math.pi)

def N(d):
    ''' Cumulative density function of standard normal random variable x. '''
    return quad(lambda x: dN(x), -20, d, limit=50)[0]

def d1f(St, K, t, T, r, sigma):
    ''' Black-Scholes-Merton d1 function.
        Parameters see e.g. BSM_call_value function. '''
    d1 = (math.log(St / K) + (r + 0.5 * sigma ** 2)
        * (T - t)) / (sigma * math.sqrt(T - t))
    return d1

def BSM_call_value(St, K, t, T, r, sigma):
    ''' Calculates Black-Scholes-Merton European call option value
        Parameters
    ==========
    St: float
    stock/index level at time t
    K: float
    strike price
    t: float
    valuation date
    T: float
    date of maturity/time-to-maturity if t = 0; T > t
    r: float
    constant, risk-less short rate
    sigma: float
    volatility
    Returns
    =======
    call_value: float
    European call present value at t
    '''
    d1 = d1f(St, K, t, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T - t)
    call_value = St * N(d1) - math.exp(-r * (T - t)) * K * N(d2)
    return call_value

def BSM_put_value(St, K, t, T, r, sigma):
    ''' Calculates Black-Scholes-Merton European put option value.
    Parameters
    ==========
    St: float
    stock/index level at time t
    K: float
    strike price
    t: float
    valuation date
    T: float
    date of maturity/time-to-maturity if t = 0; T > t
    r: float
    constant, risk-less short rate
    sigma: float
    volatility
    Returns
    =======
    put_value: float
    European put present value at t
    '''
    put_value = BSM_call_value(St, K, t, T, r, sigma) - St + math.exp(-r * (T - t)) * K
    return put_value

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class CMTWidget(QWidget):
    def __init__(self, model, *args):
        QWidget.__init__(self, *args)
        pal = QPalette()

        self.autoUpdate = True
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on the header to sort table")

        self.table_view = QTableView()
        self.proxy_model = PrxyModel()

        self.table_model = model
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)

        self.table_view.setPalette(pal)

        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.table_view.clicked.connect(self.showSelection)
        self.table_view.clicked.connect(self.selectRow)

        # enable sorting
        self.table_view.setSortingEnabled(True)

        self.table_view.horizontalHeader().sectionDoubleClicked.connect(self.onSectionDoubleClicked)

        tw = QTabWidget()
        twt1 = QWidget()
        twt2 = QWidget()
        tw.resize(300,200)

        tw.addTab(twt1,"Tab 1")
        tw.addTab(twt2,"Tab 2")

        twt1.layout = QVBoxLayout(self)
        pb = QPushButton("pushbutton")
        twt1.layout.addStretch(1)
        twt1.layout.addWidget(pb)
        twt1.setLayout((twt1.layout))

        K = 8000  # Strike price
        T = 1.0  # time-to-maturity
        r = 0.025  # constant, risk-free rate
        vol = 0.2  # constant volatility

        S = np.linspace(4000, 12000, 150)
        h = np.maximum(S - K, 0)  # payoff of the option
        C = [BSM_call_value(Szero, K, 0, T, r, vol) for Szero in S]  # BS call option values

        sc = FigureCanvasQTAgg(Figure(figsize=(1, 3)))
        self.sc_ax = sc.figure.subplots()
        daily = pd.read_csv("Misc/Demo/yahoofinance-INTC-19950101-20040412.csv", index_col=0, parse_dates=True)
        daily.drop('Adj Close', axis = 1, inplace = True)
        daily.reset_index(inplace=True)
        daily.index.name = 'Date'
        daily["Date"] = mdates.date2num(daily["Date"].values)
        cols = ['Date', 'Open', 'High', 'Low', 'Close']
        daily = daily[cols]

        candlestick_ohlc(self.sc_ax, daily.values, colorup="g", colordown="r", width=0.8)

        self.sc_ax.xaxis_date()
        self.sc_ax.grid(True)
        self.sc_ax.legend(loc=0)

        vs = QSplitter(Qt.Vertical)
        hs = QSplitter(Qt.Horizontal)
        vlayout = QVBoxLayout(self)
        upperPart = QHBoxLayout(self)
        hs.addWidget(self.table_view)
        hs.addWidget(sc)
        upperPart.addWidget(hs)

        vs.addWidget(hs)
        vs.addWidget(tw)
        vlayout.addWidget(vs)
        ft = QFont("Courier New", 7, QFont.Bold)
        self.table_view.setFont(ft);
        self.setLayout(vlayout)
        self.table_view.resizeColumnsToContents();

    def updateMplChart(self, cc):
        self.sc_ax.clear()
        # self.sc_ax.plot([0, 1, 2], [10, 1, 20])

        data = cc.histData
        d = {'Date': [x.date for x in data[2:]],
             'Open': [x.open for x in data[2:]],
             'High': [x.open for x in data[2:]],
             'Low': [x.open for x in data[2:]],
             'Close': [x.open for x in data[2:]],
             }

        df = pd.DataFrame(data=d)

        df.reset_index(inplace=True)
        df.index.name = 'Date'
        df["Date"] = mdates.date2num(df["Date"].values)
        cols = ['Date', 'Open', 'High', 'Low', 'Close']
        daily = df[cols]

        candlestick_ohlc(self.sc_ax, daily.values, colorup="g", colordown="r", width=0.8)

        # for d in data:
        #     print("%s %f %f %f %f %f")
        self.update()

    def getSelectedRow(self):
        indexes = self.table_view.selectionModel().selectedRows()

        for index in sorted(indexes):
            index = self.proxy_model.mapToSource(index)
            cc = self.table_model.bwl[str(((index.row() * 2) + Misc.const.INITIALTTICKERID))]
            print('Row %d is selected' % index.row())
            return cc

        return None

    def changeFont(self, font):
         #ft = QFont("Times", 12, QFont.Bold)
        self.table_view.setFont(font)
        self.table_view.resizeColumnsToContents()
        self.table_view.update()

    def onSectionDoubleClicked(self, logicalIndex):
        self.table_view.hideColumn(logicalIndex)
        print("onSectionDoubleClicked:", logicalIndex)

    def resetAllColumns(self):
        for ci, col in enumerate(covered_call.columns_hidden()):
            if col == True:
                self.table_view.hideColumn((ci))

    def showAllColumns (self, l):
        for col in range(l):
            self.table_view.showColumn(col)

    def clearSelection(self):
        self.table_view.clearSelection()

    def showSelection(self, item):
        cellContent = item.data()
        # print(cellContent)  # test
        sf = "You clicked on {}".format(cellContent)
        # display in title bar for convenience
        self.setWindowTitle(sf)

    def selectRow(self, index):
        # print("current row is %d", index.row())
        pass
