from PyQt5.QtGui import QPalette, QColor

APPLICATION_NAME    = "IBPY"
COMPANY_NAME        = "MITEC"
BIDSIZE     = "0"
BIDPRICE    = "1"
ASKPRICE    = "2"
ASKSIZE     = "3"
LASTPRICE   = "4"
LASTSIZE    = "5"

DATADIR     = "C:/importantData/data"

CANDLEWIDTH1    = "1_min"
CANDLEWIDTH5    = "5_min"
CANDLEWIDTH60    = "60_min"

DOWNSPL1TO5 = 1
DOWNSPL5TO12    = 2

IBPORT      = 4002

INITIALTTICKERID = 4100
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

COL_TIMEVALCHANGEPCT        =  0
COL_SYMBOL                  =  1
COL_CAPPART                 =  2
COL_INDUSTRY                =  3
COL_ROLLED                  =  4
COL_POSITION                =  5
COL_DURATION                =  6
COL_STRIKE                  =  7
COL_EXPIRY                  =  8
COL_EARNGSCALL              =  9
COL_STATUS                  =  10
COL_ULINIT                  =  11
COL_OPTINIT                  = 12
COL_BWPRICE                 =  13
COL_BWPNOW                  =  14
COL_BWPPROF                 =  15
COL_BWPPL                   =  16
COL_ULLAST                  =  17
COL_ULLMINUSBWP             =  18
COL_ULLMINUSSTRIKE          =  19
COL_ULLCHANGE               =  20
COL_ULLCHANGEPCT            =  21
COL_ULBID                   =  22
COL_ULASK                   =  23
COL_OPLAST                  =  24
COL_OPBID                   =  25
COL_OPASK                   =  26
COL_INITINTRNSCVAL          =  27
COL_INITINTRNSCVALDOLL      =  28
COL_INITTIMEVAL             =  29
COL_INITTIMEVALDOLL         =  30
COL_CURRINTRNSCVAL          =  31
COL_CURRINTRNSCVALDOLL      =  32
COL_CURRTIMEVAL             =  33
COL_CURRTIMEVALDOLL         =  34
COL_DOWNSIDEPROTECTPCT      =  35
COL_UPSIDEPOTENTIALPCT      =  36
COL_TIMEVALPROFIT           =  37
COL_ID                      =  38
COL_REALIZED                =  39
COL_ULUNREALIZED            =  40
COL_TOTAL                   =  41
