import os
import pandas as pd
import datetime

import Misc.const

mode = Misc.const.DOWNSPL5TO12

if mode == Misc.const.DOWNSPL5TO12:
    modulo = 12
    orgdir = "5_min"
    dstdir = "60_min"
elif mode == Misc.const.DOWNSPL1TO5:
    modulo = 5
    orgdir = "1_min"
    dstdir = "5_min"

cols = ['date', 'open', 'high', 'low', 'close']
paths = [ os.path.join(r"C:\git\ibpy\ibclient\data\STK_MIDPOINT",orgdir), os.path.join(r"C:\git\ibpy\ibclient\data\OPT_MIDPOINT", orgdir) ]
for path in paths:
    os.chdir(path)

    newdir=""
    for p,n,f in os.walk(os.getcwd()):
        print(p)
        newdir = p.replace(orgdir, dstdir)
        os.makedirs(newdir, exist_ok=True)
        for a in f:
            a = str(a)
            if a.endswith('.csv'):
                if os.path.exists(os.path.join(newdir,a)):
                    continue
                dfin = pd.read_csv(os.path.join(p,a))
                dfout = pd.DataFrame(columns = cols)
                rowout=[]
                i = 0
                for index, row in dfin.iterrows():
                    if index%modulo == 0:
                        min = 500000
                        max = -500000
                        rowout.append(row['date'])
                        rowout.append(row['open'])

                    tmpts = datetime.strptime(row['date'], format="%Y&m%d  %H%M%S")
                    if tmpts.minute % modulo != 0:
                        continue

                    for colname in cols:
                        if colname == 'date':
                            continue
                        if row[colname] < min:
                            min = row[colname]
                        if row[colname] > max:
                            max = row[colname]

                    if index%modulo == modulo-1:
                        rowout.append(max)
                        rowout.append(min)
                        rowout.append(row['close'])

                        dfout.loc[i] = rowout
                        rowout=[]
                        i = i + 1

            dfout.to_csv(os.path.join(newdir,a), index=False)



