import threading
from datetime import datetime, time, timedelta

from globals import globvars
import const

def run_loop():
    globvars.ibapp.run()

class BrkConnection:

    @staticmethod
    def is_time_between(begin_time, end_time, check_time=None):
        # If check time is not given, default to current UTC time
        check_time = check_time or datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:  # crosses midnight
            return check_time >= begin_time or check_time <= end_time

    @staticmethod
    def find_last_sx_opening_time(which_stockexchange: int):
        today = datetime.today()
        tod = datetime.now().time()
        weekday = datetime.weekday(today)  # 6=sunday, 0=monday

        if which_stockexchange == const.STOCKEXCHANGE_NYSE:
            opening_hour = time(10, 00, 00, 00)
            closing_hour = time(2, 00, 00, 00)
            seIsOpen = BrkConnection.is_time_between(time(10, 00), time(22,
                                                          00)) and datetime.today().weekday() >= 0 and datetime.today().weekday() < 6
            if seIsOpen:
                return datetime.now()
        else:
            closing_hour = time(22, 00, 00, 00)
            opening_hour = time(15, 30, 00, 00)

            seIsOpen = BrkConnection.is_time_between(time(15, 30), time(22, 00)) and datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            if seIsOpen:
                return datetime.now()

        if weekday == 0:  # monday
            if tod < opening_hour:  # monday morning
                return datetime.combine(today - timedelta(2), closing_hour)
            if tod > closing_hour:  # monday night
                return datetime.combine(today, closing_hour)

        if weekday >= 1 or weekday <= 4:
            if tod < opening_hour:  # tuesday to friday morning
                return datetime.combine(today, closing_hour)
            if tod > closing_hour:  # tuesday to friday night
                return datetime.combine(today, closing_hour)

        if weekday == 5:  # saturday
            return datetime.combine(today, closing_hour)

        if weekday == 6:  # sunday
            return datetime.combine(today - timedelta(1), closing_hour)

    def connectToIBKR(self):
        globvars.ibapp.connect('127.0.0.1', const.IBPORT, const.IBCLIENTID)
        api_thread = threading.Thread(target=run_loop, daemon=True)
        api_thread.start()

        globvars.ibapp.reqAccountUpdates(True, const.ACCOUNTNUMBER)

        dtnyse = BrkConnection.find_last_sx_opening_time(const.STOCKEXCHANGE_NYSE)
        ifdtnyse = dtnyse.strftime("%Y%m%d %H:%M:%S")

        dtcboe = BrkConnection.find_last_sx_opening_time(const.STOCKEXCHANGE_CBOE)
        ifdtcboe = dtcboe.strftime("%Y%m%d %H:%M:%S")

        for cc in globvars.bwl:
            if cc == globvars.bwl[-1]:
                break;

            globvars.logger.info("querying no. %s: %s", cc.bw["@id"], cc.bw["underlyer"]["@tickerSymbol"])

            # Valid Duration: S(econds), D(ay), W(eek), M(onth), Y(ear)
            # Valid Bar Sizes: 1 secs 5 secs... 1 min 2 mins, 1hour, 2 hours, 1 day, 1 week, 1 month

            globvars.ibapp.reqHistoricalData(cc.ticker_id(), cc.underlyer(), ifdtnyse, "3600 S", "5 mins", "TRADES",
                                             const.HISTDATA_OUTSIDERTH, 1, False, [])
            globvars.ibapp.reqHistoricalData(cc.ticker_id() + 1, cc.option(), ifdtcboe, "1 D", "1 hour", "MIDPOINT", 1,
                                             1, False, [])

        for cc in globvars.bwl:
            if cc == globvars.bwl[-1]:
                break;

            globvars.logger.info("querying no. %s: %s", cc.bw["@id"], cc.bw["underlyer"]["@tickerSymbol"])

            nyseIsOpen = BrkConnection.is_time_between(time(10, 00), time(22,
                                                            00)) and datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            cboeIsOpen = BrkConnection.is_time_between(time(15, 30), time(22,
                                                            00)) and datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            if nyseIsOpen:
                globvars.ibapp.reqMktData(cc.ticker_id(), cc.underlyer(), "", False, False, [])
            if cboeIsOpen:
                globvars.ibapp.reqMktData(cc.ticker_id() + 1, cc.option(), "", False, False, [])

    def disconnectFromIBKR(self):
        globvars.ibapp.disconnect()

    def clearLiveData(self):
        for cc in globvars.bwl:
            if cc == globvars.bwl[-1]:
                break;

            cc.tickerData["ullst"] = 0.0

