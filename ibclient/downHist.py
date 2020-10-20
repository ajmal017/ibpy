import os,datetime
import subprocess

stkarray = [ "TSLA","MRCY"]
expiries= [ "20201120","20201218"]
port = "4002"
startdate=20200701
enddate=20201017

symbols = [ "AMZN", "IBKR", "V", "MY", "MSCI"]

securities = [

            {"symbol"  : "JD",
             "strikes" : ["78"],
             "expiry"  : [ "20201030","20201120"]},

            {"symbol": "WDAY",
             "strikes": ["220"],
             "expiry": ["20201030", "20201120", "20201218"]},

            {"symbol": "TSM",
             "strikes": ["88", "90", "92"],
             "expiry": ["20201030", "20201218"]},

]

main="C:\git\ibpy\ibclient\Model\download.py"

for sc in securities:
    s = sc["symbol"]
    subprocess.call(
        ["py", main, '--port', port, '--security-type', 'STK', '--size', '1 min', '--start-date', '20200601',
         '--end-date', '20201017', '--data-type', 'MIDPOINT', s])
    for strik in sc["strikes"]:
        for expir in sc["expiry"]:
            subprocess.call(["py", main, '--port', port, '--security-type', 'OPT', '--size', '1 min', '--start-date', '20200601', '--end-date', '20201017',  '--data-type', 'MIDPOINT',  '--expiry', expir, '--strike', strik, s])


