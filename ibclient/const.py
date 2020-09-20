from PyQt5.QtGui import QPalette, QColor

BIDSIZE     = "0"
BIDPRICE    = "1"
ASKPRICE    = "2"
ASKSIZE     = "3"
LASTPRICE   = "4"
LASTSIZE    = "5"

#TWS Realtrading
IBPORT      = 7495

#TWS Papertrading
#IBPORT      = 7497

#GW Realtrading:
#IBPORT      = 4001

#GW Papertrading:
#IBPORT      = 4002

IBCLIENTID  = 1
ACCOUNTNUMBER = "U706599"

WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
RED = QColor(255, 0, 0)
PRIMARY = QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY = QColor(42, 130, 218)

STOCKEXCHANGE_NYSE = 0
STOCKEXCHANGE_CBOE = 1

HISTDATA_OUTSIDERTH = 0
HISTDATA_INSIDERTH = 1

COL_ID                      =  0
COL_SYMBOL                  =  1
COL_INDUSTRY                =  2
COL_ROLLED                  =  3
COL_POSITION                =  4
COL_STRIKE                  =  5
COL_EXPIRY                  =  6
COL_EARNGSCALL              =  7
COL_STATUS                  =  8
COL_ULINIT                  =  9
COL_OPTINIT                  = 10
COL_BWPRICE                 =  11
COL_BWPNOW                  =  12
COL_BWPPROF                 =  13
COL_BWPPL                   =  14
COL_ULLAST                  =  15
COL_ULLMINUSBWP             =  16
COL_ULLMINUSSTRIKE          =  17
COL_ULLCHANGE               =  18
COL_ULLCHANGEPCT            =  19
COL_ULBID                   =  20
COL_ULASK                   =  21
COL_OPLAST                  =  22
COL_OPBID                   =  23
COL_OPASK                   =  24
COL_INITINTRNSCVAL          =  25
COL_INITINTRNSCVALDOLL      =  26
COL_INITTIMEVAL             =  27
COL_INITTIMEVALDOLL         =  28
COL_CURRINTRNSCVAL          =  29
COL_CURRINTRNSCVALDOLL      =  30
COL_CURRTIMEVAL             =  31
COL_CURRTIMEVALDOLL         =  32
COL_TIMEVALCHANGEPCT        =  33
COL_TIMEVALPROFIT           =  34
COL_REALIZED                =  35
COL_ULUNREALIZED            =  36
COL_TOTAL                   =  37
