import subprocess

port = "7495"

securities = [
            {"symbol"  : ["EBAY"],
             "strikes" : ["55"],
             "expiry"  : [ "20201030","20201106","20201113","20201120","20201218"]},

            {"symbol"  : ["AAPL"],
             "strikes" : ["120","130"],
             "expiry"  : [ "20201030","20201120","20201218"]},

            {"symbol": ["SBUX", "KMX","HEI","MCHP","CYBR","GWRE","QLYS","PGR","TER","IART"],
             "strikes": ["90", "100"],
             "expiry": ["20201120", "20201218"]},
]

main="C:\git\ibpy\ibclient\Model\download.py"

for sc in securities:
    symbs = sc["symbol"]

    for s in symbs:
        subprocess.call(
            ["py", main, '--port', port, '--security-type', 'STK', '--size', '1 min', '--start-date', '20200701',
             '--end-date', '20201019', '--data-type', 'MIDPOINT', s])
        for strik in sc["strikes"]:
            for expir in sc["expiry"]:
                subprocess.call(["py", main, '--port', port, '--security-type', 'OPT', '--size', '1 min', '--start-date', '20200701', '--end-date', '20201019',  '--data-type', 'MIDPOINT',  '--expiry', expir, '--strike', strik, s])


