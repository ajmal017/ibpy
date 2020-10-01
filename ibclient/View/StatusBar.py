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
        self.apiUpdateCounterLabel = QLabel("ApiUpdate")
        self.dtlbl = QLabel("")

        self.addPermanentWidget(QLabel("NLQ:"))
        self.addPermanentWidget(self.nlqInfo)
        self.addPermanentWidget(QLabel("MRG:"))
        self.addPermanentWidget(self.mrgInfo)
        self.addPermanentWidget(QLabel("CNT:"))
        self.addPermanentWidget(self.apiUpdateCounterLabel)
        self.addPermanentWidget(self.dtlbl)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20000)

    def update(self):
        if globvars.connectionState == "CONNECTED":
            self.dtlbl.setText(datetime.now().strftime("%H:%M:%S"))
            act = self.controller.model.account
            if "NetLiquidation" in act.accountData:
                self.showMessage("last acctupdate: "+act.accountData["lastUpdate"])
                self.nlqInfo.setText(str(act.accountData["NetLiquidation"]))
                self.mrgInfo.setText(str(act.accountData["FullInitMarginReq"]))
                self.apiUpdateCounterLabel.setText(str(act.updateCounter))


