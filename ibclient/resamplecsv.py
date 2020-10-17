import os
import pandas as pd

cols = ['date', 'open', 'high', 'low', 'close']
paths = [ r"C:\git\ibpy\ibclient\data\STK_MIDPOINT\5_min", r"C:\git\ibpy\ibclient\data\OPT_MIDPOINT\5_min" ]
for path in paths:
    os.chdir(path)

    newdir=""
    for p,n,f in os.walk(os.getcwd()):
        print(p)
        newdir = p.replace("5_min", "60_min")
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
                    if index%12 == 0:
                        min = 500000
                        max = -500000
                        rowout.append(row['date'])
                        rowout.append(row['open'])

                    for colname in cols:
                        if colname == 'date':
                            continue
                        if row[colname] < min:
                            min = row[colname]
                        if row[colname] > max:
                            max = row[colname]

                    if index%12 == 11:
                        rowout.append(max)
                        rowout.append(min)
                        rowout.append(row['close'])

                        dfout.loc[i] = rowout
                        rowout=[]
                        i = i + 1

            dfout.to_csv(os.path.join(newdir,a), index=False)



