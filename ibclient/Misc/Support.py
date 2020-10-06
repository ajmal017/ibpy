from datetime import datetime, time, timedelta

import Misc.const as const

class Support:
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
            closing_hour = time(22, 00, 00, 00)
            seIsOpen = Support.is_time_between(opening_hour, closing_hour) and \
                       datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            if seIsOpen:
                return datetime.now()
        else:
            opening_hour = time(15, 30, 00, 00)
            closing_hour = time(22, 00, 00, 00)

            seIsOpen = Support.is_time_between(opening_hour, closing_hour) and \
                       datetime.today().weekday() >= 0 and datetime.today().weekday() < 5
            if seIsOpen:
                return datetime.now()

        if weekday == 0:  # monday
            if tod < opening_hour:  # monday morning
                return datetime.combine(today - timedelta(2), closing_hour)
            if tod > closing_hour:  # monday night
                return datetime.combine(today, closing_hour)

        if weekday >= 1 and weekday <= 4:
            if tod < opening_hour:  # tuesday to friday morning
                return datetime.combine(today-timedelta(1), closing_hour)
            if tod > closing_hour:  # tuesday to friday night
                return datetime.combine(today, tod)

        if weekday == 5:  # saturday
            return datetime.combine(today - timedelta(1), closing_hour)

        if weekday == 6:  # sunday
            return datetime.combine(today - timedelta(2), closing_hour)
