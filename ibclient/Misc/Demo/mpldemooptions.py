import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from Logs import logger as logger
from Misc.globals import globvars

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def calc_timevalue(row, strike):
    sval = (row['SHigh'] + row['SLow'])/2
    oval = (row['OHigh'] + row['OLow'])/2

    if sval < strike:
        tv = oval
    else:
        tv = oval - (sval-strike)
    return tv


globvars.init_globvars()
logger = logger.initMainLogger()

sdatadf = pd.read_csv("../../Model/Cache/RGEN.csv", index_col=0)
#odtaadf = pd.read_csv("../../Model/Cache/RGEN20201016.csv", index_col=0)
odtaadf = pd.read_csv("../../Model/Cache/RGEN20201120.csv", index_col=0)
cols = ['Date', 'Open', 'High', 'Low', 'Close']
sdatadf.columns = cols
odtaadf.columns = cols

comb = sdatadf.merge(odtaadf, on=['Date'])
comb.columns=['Date','SOpen','SHigh','SLow', 'SClose','OOpen','OHigh','OLow','OClose']
comb['timevalue'] = comb.apply (lambda row: calc_timevalue(row,150), axis=1)

fig, ax = plt.subplots(1, 1)

cols = ['Date', 'Open', 'High', 'Low', 'Close']
candlestick_ohlc(ax, sdatadf[cols].values, colorup='#77d879', colordown='#db3f3f', width=0.001)

ax.plot(comb['Date'],(comb['SLow'] + comb['SHigh'])/2, color='r')
ax2 = ax.twinx()
ax2.plot(comb['Date'],(comb['OLow']+comb['OHigh'])/2, color='b')

ax3 = ax2.twinx()
ax3.plot(comb['Date'], comb['timevalue'])

