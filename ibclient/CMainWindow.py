import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMenu, QLabel, QColorDialog, QFontDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from CMTWidget import CMTWidget
from globals import globvars
from BrkConnection import BrkConnection

class CMainWindow(QMainWindow):
    def __init__(self, dataList, account):
        super().__init__()

        self.statusbar = self.statusBar()
        self.setStatusBar(self.statusbar)
        self.dataList = dataList
        self.account = account

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStatusBar)
        self.timer.start(10000)


    def updateStatusBar(self):
        profstr = ""
        if "NetLiquidation" in self.account.accountData:

            profstr += "NLQ: "
            profstr += self.account.accountData["NetLiquidation"] + " CHF | "
            globvars.total = 0
            for cc in globvars.bwl:
                # globvars.total = globvars.total + int((float(cc.tickerData["ullst"]) - float(cc.bw["underlyer"][
                #                                              "@price"])) * cc.position * 100 + cc.realized + cc.itv() * cc.position * 100 - cc.ctv() * cc.position * 100)


                globvars.total = globvars.total + cc.total

            #profstr += self.account.accountData["NetLiquidation"] + " CHF ("+self.account.getLastUpdateTimestamp()+") | "

        # if "NetLiquidationByCurrency" in self.account.accountData:
        #     for cncid,cnc in enumerate(self.account.accountData["NetLiquidationByCurrency"]):
        #         try:
        #             profstr += cnc + " | "
        #             profstr += " "
        #         except:
        #             pass
        #
        # profstr += " TVP: ALL "
        # profstr += "{:.2f}".format(globvars.tvprofit)
        #
        # if "FullInitMarginReq" in self.account.accountData:
        #     profstr += " InitMargin "
        #     profstr += self.account.accountData["FullInitMarginReq"]
        #
        self.statusbar.showMessage(profstr)# + " " + "{:.2f}".format(globvars.total))

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        tauAct = cmenu.addAction("toggleAutoUpdate")
        openAct = cmenu.addAction("Show All Columns")
        resetColumnState = cmenu.addAction("Reset Columns")
        clearSelection = cmenu.addAction("Clear Selection")

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == tauAct:
            self.cmtw.toggleAutoUpdate()
        elif action == openAct:
            self.cmtw.showAllColumns()
        elif action == resetColumnState:
            self.cmtw.resetAllColumns()
        elif action == clearSelection:
            self.cmtw.clearSelection()

    def openColorDialog(self):
        c = QColorDialog.getColor()
        return c

    def openFontDialog(self):
        f = QFontDialog.getFont()
        return f

    def openSettingsDialog(self):
        pass

    def initUI(self, ccd):

        self.cmtw = CMTWidget(self.dataList, ccd)

        self.broker = BrkConnection()

        self.setCentralWidget(self.cmtw)

        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        # colorDemoAct = QAction(QIcon('exit24.png'), 'ColorDemo', self)
        # colorDemoAct.setShortcut('Ctrl+Q')
        # colorDemoAct.setStatusTip('Show all Colorss')
        # colorDemoAct.triggered.connect(open_color_demo)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        actionSelectFont = QAction(QIcon('icons/Digital - Zero.png'), 'Flee the Scene', self)
        actionSelectFont.setToolTip("Select Font")
        actionSelectFont.triggered.connect(self.openFontDialog)

        actionSelectColor = QAction(QIcon('icons/Digital - One.png'), 'Flee the Scene', self)
        actionSelectColor.setToolTip("Select Color")
        actionSelectColor.triggered.connect(self.openColorDialog)

        actionConnectToBrkApi = QAction(QIcon('icons/Link - 01.png'), 'Connect', self)
        actionConnectToBrkApi.setToolTip("Connect toIBKR")
        actionConnectToBrkApi.triggered.connect(self.broker.connectToIBKR)

        actionDisconnectFromBrkApi = QAction(QIcon('icons/Link - 02.png'), 'Disconnect', self)
        actionDisconnectFromBrkApi.setToolTip("Disconnect from IBKR")
        actionDisconnectFromBrkApi.triggered.connect(self.broker.disconnectFromIBKR)

        actionOpenSettings = QAction(QIcon('icons/Gear.png'), 'Disconnect', self)
        actionOpenSettings.setToolTip("Open Settings")
        actionOpenSettings.triggered.connect(self.openSettingsDialog)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(actionSelectFont)
        toolbar.addAction(actionSelectColor)
        toolbar.addAction(actionConnectToBrkApi)
        toolbar.addAction(actionDisconnectFromBrkApi)
        toolbar.addAction(actionOpenSettings)

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Covered Call Analyzer Application')
        self.cmtw.resetAllColumns()


    def closeEvent(self, event):
        print('Calling')
        globvars.ibapp.disconnect()
        print('event: {0}'.format(event))
        event.accept()


