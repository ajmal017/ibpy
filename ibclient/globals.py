import datetime
import time
import const
from collections import OrderedDict

class Sleep:

    def __init__(self, wait):
        self.wait = wait

    def __enter__(self):
        self.start = self.__t()
        self.finish = self.start + self.wait

    def __exit__(self, type, value, traceback):
        while self.__t() < self.finish:
            time.sleep(1. / 1000.)

    def __t(self):
        return int(round(time.time() * 1000))

class globvars:

    gfinish                     = None
    ofinish                     = None
    tfinish                     = None
    finish                     = None
    testscriptcounter           = None
    opcconnecting               = None
    currenttestscript           = None
    testisrunning               = None
    currenttestscriptlinenbr    = None
    currenttestline             = None
    doaborttesting              = None
    testingaborted              = None
    gstaborted                  = None
    currentlinecount            = None
    abortTesting                = None
    abortGst                    = None
    testispaused                = None
    test_start_time             = None
    x                           = None
    background_image            = None
    imgs                        = None
    opcconnected                = None
    imagecounter                = None
    sleepmodcntr                = None

    #statevariables
    opcprevstate                = None
    opcstate                    = None
    testprevstate               = None
    teststate                   = None
    logfilename                 = None

    opc_status_display_tooltip  = None
    tst_status_display_tooltip  = None
    gst_status_display_tooltip  = None
    pol_status_display_tooltip  = None
    tickerData                  = None
    tvprofit                    = None
    ibapi                       = None
    bwl                         = None
    cc                          = None
    header                      = None
    header1                     = OrderedDict()
    total                       = 0
    nlqInfo                   = None
    apiUpdateCounterLabel       = None
    #connectionState             = None

    def init_globvars():
        globvars.testscriptcounter           = 0
        globvars.opcconnecting               = False
        globvars.currenttestscript           = ""
        globvars.testisrunning               = False
        globvars.currenttestscriptlinenbr    = 1
        globvars.currenttestline             = ["s","h"]
        globvars.doaborttesting              = False
        globvars.testingaborted              = False
        globvars.currentlinecount            = False
        globvars.abortTesting                = False
        globvars.testispaused                = False
        globvars.test_start_time             = datetime.datetime.now()
        globvars.x                           = 0
        globvars.background_image            = None
        globvars.imgs                        = None
        globvars.opcconnected                = False
        globvars.tfinish                     = False
        globvars.ofinish                     = False
        globvars.finish                      = False
        globvars.imagecounter                = 0
        globvars.sleepmodcntr                         = 0
        globvars.logfilename                         = "mainLog.log"
        globvars.tickerData                 = {}
        globvars.logger                     = None
        globvars.tvprofit                   = 0
        globvars.total                      = 0
        globvars.ibapp                      = None
        globvars.bwl                        = []
        globvars.cc                         =  {}
        globvars.nlqInfo                  = None
        globvars.apiUpdateCounterLabel      = 0
        #globvars.connectionState            = "NOT CONNECTED"

        globvars.header1['Id'         ] = "Unique Identifier"
        globvars.header1['Symbol'     ] = "Tickersymbol of underlyer"
        globvars.header1['Ind'   ] = "Industry of Underlyer"
        globvars.header1['Rld'     ] = "How often this position was rolled"
        globvars.header1['Pos'        ] = "How many legs"
        globvars.header1['Strike'     ] = "Strike"
        globvars.header1['Expiry'     ] = "Expiry"
        globvars.header1['Earngs Call'     ] = "Next Earningscall Date"
        globvars.header1['Status'     ] = "In/Out/At the money at initiation and now ?"
        globvars.header1['UL-Init'    ] = "Price of underlyer when position was initiated"
        globvars.header1['OPT-Init'    ] = "Price of option when position was initiated"
        globvars.header1['BW-Price'   ] = "Initial buywrite price = UL-Price - Opt-premium"
        globvars.header1['BWP-Now'    ] = "Current price of this Buywrite"
        globvars.header1['BWP-Prof'   ] = "Profit of the Buywrite"
        globvars.header1['BWP-PL'     ] = ""
        globvars.header1['UL-Last'    ] = "underlyedr - last known price traded"
        globvars.header1['ULL-BWP'    ] = "UL-Last minus bwprice (for detecting when breakeven will is reached)"
        globvars.header1['ULL-STRKE'  ] = "UL-Last - Strike"
        globvars.header1['UL-Chge'    ] = "Change of UL-Price since initiation of position"
        globvars.header1['UL-Chge pct'] = ".. in pct"
        globvars.header1['UL-Bid'     ] = "last known bid for underlyer"
        globvars.header1['UL-Ask'     ] = "last known ask for underlyer"
        globvars.header1['OP-Lst'     ] = "last known trade for underlyer"
        globvars.header1['OP-Bid'     ] = "last known bid for option"
        globvars.header1['OP-Ask'     ] = "last known ask for option"
        globvars.header1['IIV'        ] = "initial intrinsic value for this option"
        globvars.header1['IIV/$'      ] = "initial intrinsic value in dollar for this option"
        globvars.header1['ITV'        ] = "initial Timevalue for this position"
        globvars.header1['ITV/$'      ] = "initial Timevalue in dollar for this position"
        globvars.header1['CIV'        ] = "Current Intrinsic Value for this position"
        globvars.header1['CIV/$'      ] = "Current Intrinsic Value in dollar for this position"
        globvars.header1['CTV'        ] = "Current TimeValue for this position"
        globvars.header1['CTV/$'      ] = "Current TimeValue in dollar for this position"
        globvars.header1['TV-Chg/%'   ] = "Change of Timevalue in %"
        globvars.header1['TV-Prof'    ] = "Accumulated timevalue profit of this position"
        globvars.header1['RLZD'       ] = "Realized from option buy back when rolling"
        globvars.header1['UL-URPNL'   ] = "Unrealizerd PNL for Unterlyer"
        globvars.header1['TOTAL'      ] = "Unrealizerd PNL for Unterlyer PLUS Realized from option buy back when rolling PLUS Accumulated timevalue profit of this position"

    def set_logger(logger):
        globvars.logger = logger

