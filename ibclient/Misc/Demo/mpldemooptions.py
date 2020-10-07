#taken from:
#http://suhasghorp.com/options-and-volatility-smile/
import time

import pandas as pd

# BSM option valuation
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.interpolate import interp2d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

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

# Test Option Payoff and Time value
K = 8000 # Strike price
T = 1.0 # time-to-maturity
r = 0.025 # constant, risk-free rate
vol = 0.2 # constant volatility

# Generate spot prices
S = np.linspace(4000, 12000, 150)
h = np.maximum(S - K, 0) # payoff of the option
C = [BSM_call_value(Szero, K, 0, T, r, vol) for Szero in S] #BS call option values

sdatadf = pd.read_csv("../../Model/Cache/RGEN.csv", index_col=0)
odtaadf = pd.read_csv("../../Model/Cache/RGEN20201016.csv", index_col=0)

#sdatadf = sdatadf.drop(sdatadf.columns[1], axis=1)

comb = sdatadf.merge(odtaadf, on=['Date'])
comb.columns=['Date','SOpen','SHigh','SLow', 'SClose','OOpen','OHigh','OLow','OClose']

plt.figure()
plt.plot(S, h, 'b-.', lw=2.5, label='payoff') # plot inner value at maturity
plt.plot(S, C, 'r', lw=2.5, label='present value') # plot option present value
plt.grid(True)
plt.legend(loc=0)
plt.xlabel('index level $S_0$')
plt.ylabel('present value $C(t=0)$')

# model parameters
S0 = 100.0 # initial index level
T = 10.0 # time horizon
r = 0.05 # risk-less short rate
vol = 0.2 # instantaneous volatility
# simulation parameters
np.random.seed(250000)
#generate a pd array with business dates, ignores holidays
gbm_dates = pd.DatetimeIndex(start='10-05-2007',end='10-05-2017',freq='B')
M = len(gbm_dates) # time steps
I = 1 # index level paths
dt = 1 / 252. # 252 business days a year
df = math.exp(-r * dt) # discount factor

# stock price paths
rand = np.random.standard_normal((M, I)) # random numbers
S = np.zeros_like(rand) # stock matrix
S[0] = S0 # initial values
for t in range(1, M): # stock price paths using Eq.5
    S[t] = S[t - 1] * np.exp((r - vol ** 2 / 2) * dt + vol * rand[t] * math.sqrt(dt))
#create a pd dataframe with date as index and a column named "spot"
gbm = pd.DataFrame(S[:, 0], index=gbm_dates, columns=['spot'])
gbm['returns'] = np.log(gbm['spot'] / gbm['spot'].shift(1)) #log returns
# Realized Volatility
gbm['realized_var'] = 252 * np.cumsum(gbm['returns'] ** 2) / np.arange(len(gbm))
gbm['realized_vol'] = np.sqrt(gbm['realized_var'])
print (gbm.head())
gbm = gbm.dropna()

plt.figure(figsize=(9, 6))
plt.subplot(211)
gbm['spot'].plot()
plt.ylabel('daily quotes')
plt.grid(True)
plt.axis('tight')
plt.subplot(212)
gbm['returns'].plot()
plt.ylabel('daily log returns')
plt.grid(True)
plt.axis('tight')

time.sleep(10)

