import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pandas as pd
from scipy.integrate import quad
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mplfinance.original_flavor import candlestick_ohlc

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

class CMTWidget(QWidget):
    def __init__(self, model, controller, *args):
        QWidget.__init__(self, *args)
        pal = QPalette()

        self.autoUpdate = True
        # self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on header to sort table")

        self.table_view = QTableView()
        self.proxy_model = PrxyModel()

        self.table_model = model
        self.controller = controller
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)
        self.table_view.setPalette(pal)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.clicked.connect(self.showSelection)
        self.table_view.clicked.connect(self.selectRow)
        self.table_view.doubleClicked.connect(self.doubleClickedCell)

        # enable sorting
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().sectionDoubleClicked.connect(self.onSectionDoubleClicked)

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.table_view)
        # self.current_font = QFont("Arial Black", 10)
        self.current_font = QFont("Cooper Black", 9)
        self.table_view.setFont(self.current_font);
        self.setLayout(vlayout)
        self.table_view.resizeColumnsToContents();

    def setPositionViewer(self,p):
        self.positionViewer =   p

    def getSelectedRow(self):
        indexes = self.table_view.selectionModel().selectedRows()

        for index in sorted(indexes):
            index = self.proxy_model.mapToSource(index)
            cc = self.table_model.bwl[str(((index.row() * 2) + Misc.const.INITIALTTICKERID))]
            return cc

        return self.table_model.bwl["4100"]

    def changeFont(self, font):
        self.current_font = font
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
        sf = "You clicked on {}".format(cellContent)
        self.setWindowTitle(sf)

    def selectRow(self, index):
        pass

    def doubleClickedCell(self, idx):
        index = self.proxy_model.mapToSource(idx)
        r = index.row()
        c = index.column()
        cc = self.proxy_model.sourceModel().bwl[str(((r * 2) + Misc.const.INITIALTTICKERID))]
        sym = cc.statData.buyWrite["underlyer"]["@tickerSymbol"]
        print ("clicked on ",sym," ",int(c))
        if c == 1:
            a = self.controller.getStockData(cc)
            self.positionViewer.updateMplChart(cc, a)

