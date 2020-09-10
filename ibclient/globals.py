import datetime
import time
import const

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
        globvars.accountData                     = {}
        globvars.tvprofit                   = 0
        globvars.ibapp                      = None

        globvars.bwl                        = []
        globvars.cc                        =  {}
        globvars.header                     = ['Id', 'Symbol', 'Industry', 'Pos', 'Strike', 'Expiry', 'Status', 'UL-Init', 'BW-Price', 'UL-Last', 'UL-Chge',
         'UL-Chge pct', 'UL-Bid', 'UL-Ask', 'OP-Lst', 'OP-Bid', 'OP-Ask', 'ITV', 'ITV/$', 'CTV', 'CTV/$', 'TV-Chg', 'TV-Prof']

    def set_logger(logger):
        globvars.logger = logger

