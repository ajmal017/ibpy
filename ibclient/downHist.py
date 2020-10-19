import os,datetime
import subprocess

stkarray = [ "TSLA","MRCY"]
expiries= [ "20201120","20201218"]
port = 4001
startdate=20200701
enddate=20201017

symbols = [ "AMZN", "IBKR", "V", "MY", "MSCI"]

securities = [

            {"symbol"  : "AMZN",
             "strikes" : ["3300","3400","3500"],
             "expiry"  : [ "20201120","20201218"]},

            # {"symbol"  : "IBKR",
            #  "strikes" : ["45", "50", "55"],
            #  "expiry"  : ["20201120", "20201218"]},
]

main="C:\git\ibpy\ibclient\Model\download.py"

for sc in securities:
    s = sc["symbol"]
    subprocess.call(
        ["py", main, '--port', '4002', '--security-type', 'STK', '--size', '1 min', '--start-date', '20200601',
         '--end-date', '20201017', '--data-type', 'MIDPOINT', s])
    for strik in sc["strikes"]:
        for expir in sc["expiry"]:
            subprocess.call(["py", main, '--port', '4002', '--security-type', 'OPT', '--size', '1 min', '--start-date', '20200601', '--end-date', '20201017',  '--data-type', 'MIDPOINT',  '--expiry', expir, '--strike', strik, s])


