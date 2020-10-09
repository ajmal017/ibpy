from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMenu, QLabel, QColorDialog, QFontDialog, QStatusBar
from PyQt5.QtCore import QTimer

from Misc.globals import globvars

class StatusBar(QStatusBar):
    def __init__(self, ctrl, parent = None):
        super(StatusBar, self).__init__(parent)
        self.controller = ctrl
        self.nlqInfo = QLabel("NLQINFORMATION")
        self.mrgInfo = QLabel("NLQINFORMATION")
        self.totalInfo = QLabel("--PROFIT--")
        self.totalCtv = QLabel("--TCTV--")
        self.totalItv = QLabel("--TITV--")
        self.tvdiff   = QLabel("--TDIFF--")
        self.apiUpdateCounterLabel = QLabel("ApiUpdate")
        self.dtlbl = QLabel("")

        self.addPermanentWidget(QLabel("ITV-CTV:"))
        self.addPermanentWidget(self.tvdiff)
        self.addPermanentWidget(QLabel("CTV:"))
        self.addPermanentWidget(self.totalCtv)
        self.addPermanentWidget(QLabel("ITV:"))
        self.addPermanentWidget(self.totalItv)
        self.addPermanentWidget(QLabel("PNL:"))
        self.addPermanentWidget(self.totalInfo)
        self.addPermanentWidget(QLabel("NLQ:"))
        self.addPermanentWidget(self.nlqInfo)
        self.addPermanentWidget(QLabel("MRG:"))
        self.addPermanentWidget(self.mrgInfo)
        self.addPermanentWidget(QLabel("CNT:"))
        self.addPermanentWidget(self.apiUpdateCounterLabel)
        self.addPermanentWidget(self.dtlbl)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10000)

    def update(self):
        globvars.lock.acquire()
        if globvars.connectionState == "CONNECTED":
            self.dtlbl.setText(datetime.now().strftime("%H:%M:%S"))
            act = self.controller.model.account
            if "NetLiquidation" in act.accountData:
                self.showMessage("last acctupdate: "+act.accountData["lastUpdate"])
                self.nlqInfo.setText(str(act.accountData["NetLiquidation"]))
                self.mrgInfo.setText(str(act.accountData["FullInitMarginReq"]))
                self.totalCtv.setText("{:.2f}".format((globvars.totalCtv)))
                self.totalItv.setText("{:.2f}".format((globvars.totalItv)))
                self.totalInfo.setText("{:.2f}".format((globvars.total)))
                self.tvdiff.setText("{:.2f}".format((globvars.totalItv - globvars.totalCtv)))
                self.apiUpdateCounterLabel.setText(str(act.updateCounter))
        globvars.lock.release()



