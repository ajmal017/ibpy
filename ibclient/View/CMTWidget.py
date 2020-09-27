import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pandas as pd
from scipy.integrate import quad
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, FigureCanvas, NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

import numpy as np

from Model.CMTModel import CMTModel, PrxyModel
from Controller.covcall import covered_call

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

        # sc = MplCanvas(self, width=2, height=4, dpi=100)
        #sc = FigureCanvasQTAgg(Figure(figsize=(5, 3)))

        sc = FigureCanvasQTAgg(Figure(figsize=(1, 3)))

        sc_ax = sc.figure.subplots()

        #1)
        # sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])

        #2)
        # sc.axes.plot(S, h, 'b-.', lw=2.5, label='payoff')  # plot inner value at maturity
        # sc.axes.plot(S, C, 'r', lw=2.5, label='present value')  # plot option present value
        # sc.axes.grid(True)
        # sc.axes.grid(True)
        # sc.axes.legend(loc=0)
        # sc.axes.xlabel('index level $S_0$')
        # sc.axes.ylabel('present value $C(t=0)$')

        #3)
        # model parameters

        # model parameters
        S0 = 100.0  # initial index level
        T = 10.0  # time horizon
        r = 0.05  # risk-less short rate
        vol = 0.2  # instantaneous volatility
        # simulation parameters
        np.random.seed(250000)
        # generate a pd array with business dates, ignores holidays
        gbm_dates = pd.DatetimeIndex(start='10-05-2007', end='10-05-2017', freq='B')
        M = len(gbm_dates)  # time steps
        I = 1  # index level paths
        dt = 1 / 252.  # 252 business days a year
        df = math.exp(-r * dt)  # discount factor

        # stock price paths
        rand = np.random.standard_normal((M, I))  # random numbers
        S = np.zeros_like(rand)  # stock matrix
        S[0] = S0  # initial values
        for t in range(1, M):  # stock price paths using Eq.5
            S[t] = S[t - 1] * np.exp((r - vol ** 2 / 2) * dt + vol * rand[t] * math.sqrt(dt))
        # create a pd dataframe with date as index and a column named "spot"
        gbm = pd.DataFrame(S[:, 0], index=gbm_dates, columns=['spot'])
        gbm['returns'] = np.log(gbm['spot'] / gbm['spot'].shift(1))  # log returns
        # Realized Volatility
        gbm['realized_var'] = 252 * np.cumsum(gbm['returns'] ** 2) / np.arange(len(gbm))
        gbm['realized_vol'] = np.sqrt(gbm['realized_var'])
        print(gbm.head())
        gbm = gbm.dropna()

        #t = np.linspace(0, 10, 501)
        # sc_ax.plot(t, np.tan(t), ".")

        t = np.linspace(1, M, 2610)
        sc_ax.plot(t, S, ".")

        # sc.axes.figure(figsize=(9, 6))
        #sc.subplot(211)
        #gbm['spot'].plot()
        #sc.axes.ylabel('daily quotes')
        # sc.axes.grid(True)
        # sc.axes.axis('tight')
        # #sc.axes.subplot(212)
        # gbm['returns'].plot()
        # #sc.axes.ylabel('daily log returns')
        # sc.axes.grid(True)
        # sc.axes.axis('tight')

        #end of 3)





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
