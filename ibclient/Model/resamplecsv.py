import os
import pandas as pd
import datetime
import argparse

import  Misc.const

def resample(mode, ow, symbols):

    if mode == "1TO5":
        modulo = 5
        orgdir = "1_min"
        dstdir = "5_min"
    else:
        modulo = 12
        orgdir = "5_min"
        dstdir = "60_min"

    cols = ['date', 'open', 'high', 'low', 'close']

    paths = [ os.path.join(Misc.const.DATADIR, "STK_MIDPOINT",orgdir), os.path.join(Misc.const.DATADIR, "OPT_MIDPOINT", orgdir) ]
    for path in paths:
        os.chdir(path)

        newdir=""
        for p,n,f in os.walk(os.getcwd()):
            docontinue = False
            if symbols[0] != "ALL":
                for s in symbols:
                    if s in p:
                        docontinue = True
                if docontinue == False:
                    continue

            print(p)
            newdir = p.replace(orgdir, dstdir)
            os.makedirs(newdir, exist_ok=True)
            for a in f:
                a = str(a)
                b=a.split(".")[0]
                date = datetime.datetime.strptime(b, "%Y%m%d")
                #6=SAT, 7=SUN
                if date.isoweekday() in [6,7]:
                    continue
                if a.endswith('.csv'):
                    if ow == False and os.path.exists(os.path.join(newdir,a)):
                        continue
                    print(a)
                    dfin = pd.read_csv(os.path.join(p,a))
                    rowout=[]
                    started = False
                    dfout = pd.DataFrame(columns=cols)
                    i = 0
                    for index, row in dfin.iterrows():
                        tmpts = datetime.datetime.strptime(row['date'], "%Y%m%d  %H:%M:%S")
                        if started == False and tmpts.minute % modulo != 0:
                            continue

                        if tmpts.minute%modulo == 0:
                            min = 500000
                            max = -500000
                            rowout.append(row['date'])
                            rowout.append(row['open'])

                        started = True

                        for colname in cols:
                            if colname == 'date':
                                continue
                            if row[colname] < min:
                                min = row[colname]
                            if row[colname] > max:
                                max = row[colname]

                        if tmpts.minute%modulo == modulo-1:
                            rowout.append(max)
                            rowout.append(min)
                            rowout.append(row['close'])
                            started = False
                            dfout.loc[i] = rowout
                            rowout=[]
                            i = i + 1
                    dfout.to_csv(os.path.join(newdir,a), index=False)

# argp = argparse.ArgumentParser()
# argp.add_argument("symbol", nargs="+")
# argp.add_argument("--overwrite", type=str, default="yes", help="bar size")
# args = argp.parse_args()
#
# if args.overwrite=="yes":
#     ow = True
# else:
#     ow = False
#
# resample("1TO5", ow, args.symbol)
# resample("5TO12", ow, args.symbol)
#
#
