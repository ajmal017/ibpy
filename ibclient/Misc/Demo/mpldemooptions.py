import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from Logs import logger as logger
from Misc.globals import globvars

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
odtaadf = pd.read_csv("../../Model/Cache/RGEN20201016.csv", index_col=0)
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
input("KEY")

# plt.figure()
# plt.plot(S, h, 'b-.', lw=2.5, label='payoff') # plot inner value at maturity
# plt.plot(S, C, 'r', lw=2.5, label='present value') # plot option present value
# plt.grid(True)
# plt.legend(loc=0)
# plt.xlabel('index level $S_0$')
# plt.ylabel('present value $C(t=0)$')
#
# # model parameters
# S0 = 100.0 # initial index level
# T = 10.0 # time horizon
# r = 0.05 # risk-less short rate
# vol = 0.2 # instantaneous volatility
# # simulation parameters
# np.random.seed(250000)
# #generate a pd array with business dates, ignores holidays
# gbm_dates = pd.DatetimeIndex(start='10-05-2007',end='10-05-2017',freq='B')
# M = len(gbm_dates) # time steps
# I = 1 # index level paths
# dt = 1 / 252. # 252 business days a year
# df = math.exp(-r * dt) # discount factor
#
# # stock price paths
# rand = np.random.standard_normal((M, I)) # random numbers
# S = np.zeros_like(rand) # stock matrix
# S[0] = S0 # initial values
# for t in range(1, M): # stock price paths using Eq.5
#     S[t] = S[t - 1] * np.exp((r - vol ** 2 / 2) * dt + vol * rand[t] * math.sqrt(dt))
# #create a pd dataframe with date as index and a column named "spot"
# gbm = pd.DataFrame(S[:, 0], index=gbm_dates, columns=['spot'])
# gbm['returns'] = np.log(gbm['spot'] / gbm['spot'].shift(1)) #log returns
# # Realized Volatility
# gbm['realized_var'] = 252 * np.cumsum(gbm['returns'] ** 2) / np.arange(len(gbm))
# gbm['realized_vol'] = np.sqrt(gbm['realized_var'])
# print (gbm.head())
# gbm = gbm.dropna()
#
# plt.figure(figsize=(9, 6))
# plt.subplot(211)
# gbm['spot'].plot()
# plt.ylabel('daily quotes')
# plt.grid(True)
# plt.axis('tight')
# plt.subplot(212)
# gbm['returns'].plot()
# plt.ylabel('daily log returns')
# plt.grid(True)
# plt.axis('tight')
#
# time.sleep(10)
#
