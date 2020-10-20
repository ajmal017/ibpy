import datetime

def humanreadable_date(dtin):
    if type(dtin) == str:
        try:
            dtout = datetime.datetime.strptime(dtin, "%Y%m%d %H:%M:%S")
        except:
            pass
    else:
        dtout = dtin

    dtout = datetime.datetime.strftime(dtout, "%m.%b %H:%M:%S")

    return dtout


