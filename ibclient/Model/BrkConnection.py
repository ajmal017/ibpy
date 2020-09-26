from datetime import datetime, time, timedelta
import threading

from Misc.globals import globvars
from Misc import const
from Misc.Support import Support

from .BrkApi import BrkApi

class BrkConnection:
    def __init__(self):
        self.initConnection()
        self.brkApi = BrkApi()

    def initConnection(self):
        globvars.connectionState = "INITIALIZED"

    def setBwData(self, td):
        self.bw = td
        self.brkApi.setBwData(td)

    def run_loop(self):
        self.brkApi.run()

    def connectToIBKR(self):
        self.brkApi.connect('127.0.0.1', const.IBPORT, const.IBCLIENTID)
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

            # globvars.logger.info("querying no. %s: %s", cc.bw["@id"], cc.bw["underlyer"]["@tickerSymbol"])

            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month
            ul = self.bw[cc].underlyer()
            op = self.bw[cc].option()
            icc = int(cc)
            icco = int(cc) + 1
            ifdtnyse = '20200924 20:00:00'
            ifdtcboe = '20200924 20:00:00'
            self.brkApi.reqHistoricalData(icc, ul, ifdtnyse, "1 D", "1 hour", "MIDPOINT",
                                             const.HISTDATA_OUTSIDERTH, 1, False, [])
            self.brkApi.reqHistoricalData(icco, op, ifdtcboe, "1 D", "1 hour", "MIDPOINT", 1,
                                             1, False, [])

        for cc in self.bw:

            # globvars.logger.info("querying no. %s: %s", cc.bw["@id"], cc.bw["underlyer"]["@tickerSymbol"])

            nyseIsOpen = Support.is_time_between(time(10, 00), time(22,
                                                            00)) and datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            cboeIsOpen = Support.is_time_between(time(15, 30), time(22,
                                                            00)) and datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            icc = int(cc)
            icco = int(cc) + 1

            if nyseIsOpen:
                self.brkApi.reqMktData(icc, self.bw[cc].underlyer(), "", False, False, [])
            if cboeIsOpen:
                self.brkApi.reqMktData(icco, self.bw[cc].option(), "", False, False, [])

    def disconnectFromIBKR(self):
        self.brkApi.disconnect()
        globvars.connectionState = "DISCONNECTED"

    def clearLiveData(self):
        for cc in globvars.bwl:
            if cc == globvars.bwl[-1]:
                break;

            cc.tickerData["ullst"] = 0.0

