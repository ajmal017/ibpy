import datetime
import time
#from datetime import datetime, time,
import threading

import pandas as pd

from Misc.globals import globvars
from Misc import const
from Misc.Support import Support

from .BrkApi import BrkApi
from collections import OrderedDict

class BrkConnection:
    def __init__(self):
        self.initConnection()
        self.brkApi = BrkApi()
        self.brokerPort = const.IBPORT

    def initConnection(self):
        globvars.connectionState = "INITIALIZED"

    def changeBrokerPort(self, newport):
        self.brokerPort = newport

    def setData(self, td, act):
        self.bw = td
        self.brkApi.setBwData(td)
        self.brkApi.setAccount(act)

    def run_loop(self):
        self.brkApi.run()

    def convert_timedelta(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return hours, minutes, seconds

    def getStockData(self, cc):

        ul = cc.underlyer()
        op = cc.option()

        dtnyse = Support.find_last_sx_opening_time(const.STOCKEXCHANGE_NYSE)
        ifdtnyse = dtnyse.strftime("%Y%m%d %H:%M:%S")

        icc = cc.tickData.tickerId
        self.brkApi.resetHistData(icc)
        self.brkApi.endflag[icc] = False

        # we must have arount 200-400 candles:
        # 1) duration in days => seconds
        candlewidthinsec = int(cc.statData.duration) * 24*3600
        widthstr = str(candlewidthinsec)+" S"

        vhbss = OrderedDict({
            "1 secs": 1,
            "5 secs": 5,
            "10 secs": 10,
            "15 secs": 15,
            "30 secs": 30,
            "1 min": 60,
            "2 mins": 120,
            "3 mins": 180,
            "5 mins": 300,
            "10 mins": 600,
            "15 mins": 900,
            "20 mins": 1200,
            "30 mins": 1800,
            "1 hour": 3600,
            "2 hours": 7200,
            "3 hours": 10800,
            "4 hours": 14400,
            "8 hours": 28800,
            "1 day": 3*28800,
            "1 W": 7*3*28800,
            "1 M": 4*7*3*28800})

        nbrOfBars = 1000
        i = 0
        while nbrOfBars > 400:
            barsizeinsecs = vhbss[list(vhbss.keys())[i]]
            nbrOfBars = candlewidthinsec/barsizeinsecs
            i = i + 1

        widthstr = list(vhbss.keys())[i-1]
        durstr = cc.statData.duration + " D"

        if icc % 2 == 0:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
            self.brkApi.reqHistoricalData(icc, ul, ifdtnyse, durstr, widthstr, "MIDPOINT",
                                          const.HISTDATA_INSIDERTH, 1, False, [])
        else:
            self.brkApi.reqHistoricalData(icc+1, op, ifdtcboe, durstr, widthstr, "MIDPOINT",
                                          const.HISTDATA_INSIDERTH, 1, False, [])

        while self.brkApi.endflag[icc] == False or self.brkApi.endflag[icc+1] == False:
            time.sleep(1)

        cc.histData =  self.brkApi.getHistData(icc)
        # cc.histData = pd.DataFrame(cc.histData)
        cc.histData.to_csv("Model/Cache/"+ul.symbol+".csv")

        cc.ophistData =  self.brkApi.getHistData(icc+1)
        # cc.ophistData = pd.DataFrame(cc.ophistData)
        cc.ophistData.to_csv("Model/Cache/"+op.symbol+op.lastTradeDateOrContractMonth+".csv")

        # datatable = pd.DataFrame(self.brkApi.getHistData(icc))
        # cc.histData = datatable
        # cc.histData.columns = ['Date', 'Open', 'High', 'Low', 'Close']

    def connectToIBKR(self):
        self.brkApi.connect('127.0.0.1', self.brokerPort, const.IBCLIENTID)
        api_thread = threading.Thread(target=self.run_loop, daemon=True)
        api_thread.start()
        globvars.connectionState = "CONNECTED"

        self.brkApi.reqAccountUpdates(True, const.ACCOUNTNUMBER)

        for cc in self.bw:
            self.brkApi.reqContractDetails(cc, self.bw[cc].underlyer())

        dtnyse = Support.find_last_sx_opening_time(const.STOCKEXCHANGE_NYSE)
        ifdtnyse = dtnyse.strftime("%Y%m%d %H:%M:%S")

        dtcboe = Support.find_last_sx_opening_time(const.STOCKEXCHANGE_CBOE)
        ifdtcboe = dtcboe.strftime("%Y%m%d %H:%M:%S")

        for cc in self.bw:
            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
            ul = self.bw[cc].underlyer()
            op = self.bw[cc].option()
            icc = int(cc)
            # ifdtnyse = '20200926 02:00:00'
            # ifdtcboe = '20200925 22:00:00'
            if icc %2 == 0:
                self.brkApi.reqHistoricalData(icc, ul, ifdtnyse, "120 S", "1 min", "MIDPOINT",
                                                 const.HISTDATA_OUTSIDERTH, 1, False, [])
            else:
                # globvars.logger.info("querying no. %s => %s", str(icco), cc.bw["underlyer"]["@tickerSymbol"])
                self.brkApi.reqHistoricalData(icc, op, ifdtcboe, "120 S", "1 min", "MIDPOINT", 1,
                                                 1, False, [])

        for cc in self.bw:

            # globvars.logger.info("querying no. %s: %s", cc.bw["@id"], cc.bw["underlyer"]["@tickerSymbol"])
            ul = self.bw[cc].underlyer()
            op = self.bw[cc].option()
            icc = int(cc)

            nyseIsOpen = Support.is_time_between(datetime.time(10, 00), datetime.time(22,
                                                            00)) and datetime.datetime.today().weekday() >= 0 and datetime.datetime.today().weekday() < 5
            cboeIsOpen = Support.is_time_between(datetime.time(15, 30), datetime.time(22,
                                                            00)) and datetime.datetime.today().weekday() >= 0 and datetime.datetime.today().weekday() < 5
            if icc %2 == 0:
                if nyseIsOpen:
                    self.brkApi.reqMktData(icc, self.bw[cc].underlyer(), "", False, False, [])
            else:
                if cboeIsOpen:
                    self.brkApi.reqMktData(icc, self.bw[cc].option(), "", False, False, [])

    def disconnectFromIBKR(self):
        self.brkApi.disconnect()
        globvars.connectionState = "DISCONNECTED"

    def clearLiveData(self):
        for cc in globvars.bwl:
            if cc == globvars.bwl[-1]:
                break;

            cc.tickerData["ullst"] = 0.0

