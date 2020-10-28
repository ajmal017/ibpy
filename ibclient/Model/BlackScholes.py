#taken 1:1 from:
#https://github.com/YuChenAmberLu/Options-Calculator/blob/master/Options%20Calculator%20with%20Black%20Scholes%20model.ipynb

## import certain packages
from math import log, sqrt, pi, exp
from scipy.stats import norm
from datetime import datetime, date
import numpy as np
import pandas as pd
from pandas import DataFrame

# Underlying price (per share): S;
# Strike price of the option (per share): K;
# Time to maturity (years): T;
# Continuously compounding risk-free interest rate: r;
# Volatility: sigma;

## define two functions, d1 and d2 in Black-Scholes model
def d1(S,K,T,r,sigma):
    return(log(S/K)+(r+sigma**2/2.)*T)/sigma*sqrt(T)
def d2(S,K,T,r,sigma):
    return d1(S,K,T,r,sigma)-sigma*sqrt(T)

## define the call options price function
def bs_call(S,K,T,r,sigma):
    return S*norm.cdf(d1(S,K,T,r,sigma))-K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma))

## define the put options price function
def bs_put(S,K,T,r,sigma):
    return K*exp(-r*T)-S+bs_call(S,K,T,r,sigma)

## define the Call_Greeks of an option
def call_delta(S,K,T,r,sigma):
    return norm.cdf(d1(S,K,T,r,sigma))
def call_gamma(S,K,T,r,sigma):
    return norm.pdf(d1(S,K,T,r,sigma))/(S*sigma*sqrt(T))
def call_vega(S,K,T,r,sigma):
    return 0.01*(S*norm.pdf(d1(S,K,T,r,sigma))*sqrt(T))
def call_theta(S,K,T,r,sigma):
    return 0.01*(-(S*norm.pdf(d1(S,K,T,r,sigma))*sigma)/(2*sqrt(T)) - r*K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma)))
def call_rho(S,K,T,r,sigma):
    return 0.01*(K*T*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma)))

## define the Put_Greeks of an option
def put_delta(S,K,T,r,sigma):
    return -norm.cdf(-d1(S,K,T,r,sigma))
def put_gamma(S,K,T,r,sigma):
    return norm.pdf(d1(S,K,T,r,sigma))/(S*sigma*sqrt(T))
def put_vega(S,K,T,r,sigma):
    return 0.01*(S*norm.pdf(d1(S,K,T,r,sigma))*sqrt(T))
def put_theta(S,K,T,r,sigma):
    return 0.01*(-(S*norm.pdf(d1(S,K,T,r,sigma))*sigma)/(2*sqrt(T)) + r*K*exp(-r*T)*norm.cdf(-d2(S,K,T,r,sigma)))
def put_rho(S,K,T,r,sigma):
    return 0.01*(-K*T*exp(-r*T)*norm.cdf(-d2(S,K,T,r,sigma)))

## to calculate the volatility of a put/call option
def implied_volatility(Price,S,K,T,r,O):
    sigma = 0.001
    # print (np.array([['Price', 'S', 'K', 'T', 'r'], [Price, S, K, T, r]]))
    if O == 'C':
        i=0
        while sigma < 1:
            i = i + 1
            Price_implied = S*norm.cdf(d1(S,K,T,r,sigma))-K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma))
            print(i," ",Price_implied)
            if Price-(Price_implied) < 0.001:
                return sigma
            sigma += 0.001
        return "It could not find the right volatility of the call option."
    else:
        while sigma < 1:
            Price_implied = K*exp(-r*T)-S+bs_call(S,K,T,r,sigma)
            if Price-(Price_implied) < 0.001:
                return sigma
            sigma += 0.001
        return "It could not find the right volatility of the put option."
    return

if __name__ == "__main__":
    ## input the current stock price and check if it is a number.
    S = input("What is the current stock price? ");
    while True:
        try:
            S = float(S)
            break
        except:
            print("The current stock price has to be a NUMBER.")
            S = input("What is the current stock price? ")

    ## input the strike price and check if it is a number.
    K = input("What is the strike price? ");
    while True:
        try:
            K = float(K)
            break
        except:
            print("The the strike price has to be a NUMBER.")
            K = input("What is the strike price? ")


    ## input the expiration_date and calculate the days between today and the expiration date.
    while True:
        expiration_date = input("What is the expiration date of the options? (mm-dd-yyyy) ")
        try:
            expiration_date = datetime.strptime(expiration_date, "%m-%d-%Y")
        except ValueError as e:
            print("error: %s\nTry again." % (e,))
        else:
            break
    T = (expiration_date - datetime.utcnow()).days / 365


    ## input the continuously compounding risk-free interest rate and check if it is a number.
    r = input("What is the continuously compounding risk-free interest rate in percentage(%)? ");
    while True:
        try:
            r = float(r)
            break
        except:
            print("The continuously compounding risk-free interest rate has to be a NUMBER.")
            r = input("What is the continuously compounding risk-free interest rate in percentage(%)? ")

    option = input ("Put or Call option? (P/C)  ")
    while option != 'P' and option !='C' :
        print ("error: this option does not match the format (P/C) \nTry again.")
        option = input ("Put or Call option? (P/C)  ")

    Price = input("What is the option price? ");
    while True:
        try:
            Price = float(Price)
            break
        except:
            print("The the option price has to be a NUMBER.")
            Price = input("What is the option price? ")
    print ("The implied volatility is " + str (100* implied_volatility(Price,S,K,T,r)) + " %.")

    ## input the volatility and check if it is a number.
    sigma = input("What is the volatility in percentage(%)? ");
    while True:
        try:
            sigma = float(sigma)
            if sigma > 100 or sigma < 0:
                print ( "The range of sigma has to be in [0,100].")
                sigma = input("What is the volatility in percentage(%)? ")
            break
        except:
            print("The volatility has to be a NUMBER.")
            sigma = input("What is the volatility in percentage(%)? ")

    data = {'Symbol': ['S', 'K', 'T', 'r', 'sigma'],
            'Input': [S, K, T , r , sigma]}
    input_frame = DataFrame(data, columns=['Symbol', 'Input'],
                       index=['Underlying price', 'Strike price', 'Time to maturity', 'Risk-free interest rate', 'Volatility'])
    input_frame

    ## calculate the call / put option price and the greeks of the call / put option
    r = r/100; sigma = sigma/100;
    price_and_greeks = {'Call' : [bs_call(S,K,T,r,sigma), call_delta(S,K,T,r,sigma), call_gamma(S,K,T,r,sigma),call_vega(S,K,T,r,sigma), call_rho(S,K,T,r,sigma), call_theta(S,K,T,r,sigma)],
                        'Put' : [bs_put(S,K,T,r,sigma), put_delta(S,K,T,r,sigma), put_gamma(S,K,T,r,sigma),put_vega(S,K,T,r,sigma), put_rho(S,K,T,r,sigma), put_theta(S,K,T,r,sigma)]}
    price_and_greeks_frame = DataFrame(price_and_greeks, columns=['Call','Put'], index=['Price', 'delta', 'gamma','vega','rho','theta'])
    price_and_greeks_frame

