import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMenu, QLabel, QColorDialog, QFontDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from CMTWidget import CMTWidget
from globals import globvars
from BrkConnection import BrkConnection
from StatusBar import StatusBar
from datetime import datetime

class CMainWindow(QMainWindow):
    def __init__(self, dataList, account):
        super().__init__()

        globvars.nlqInfo = QLabel("NLQINFORMATION")
        globvars.mrgInfo = QLabel("NLQINFORMATION")
        globvars.apiUpdateCounterLabel = QLabel("ApiUpdate")
        self.dtlbl = QLabel("")

        self.statusBar().addPermanentWidget(QLabel("NLQ:"))
        self.statusBar().addPermanentWidget(globvars.nlqInfo)
        self.statusBar().addPermanentWidget(QLabel("MRG:"))
        self.statusBar().addPermanentWidget(globvars.mrgInfo)
        self.statusBar().addPermanentWidget(QLabel("CNT:"))
        self.statusBar().addPermanentWidget(globvars.apiUpdateCounterLabel)
        self.statusBar().addPermanentWidget(self.dtlbl)

        self.dataList = dataList
        self.account = account

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.updateStatusBar)
        # self.timer.start(1000)

    def updateStatusBar(self):
        if globvars.connectionState == "CONNECTED":
            self.dtlbl.setText(datetime.now().strftime("%H:%M:%S"))

            if "NetLiquidation" in self.account.accountData:
                self.statusBar().showMessage("last acctupdate: "+self.account.accountData["lastUpdate"])
                globvars.nlqInfo.setText(str(self.account.accountData["NetLiquidation"]))
                globvars.mrgInfo.setText(str(self.account.accountData["FullInitMarginReq"]))
                globvars.apiUpdateCounterLabel.setText(str(self.account.updateCounter))

            #self.statusBar().showMessage("now: "+datetime.now().strftime("%H:%M:%S"))
            self.statusBar().update()

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
        (font,ok) = QFontDialog.getFont()
        if ok:
            self.cmtw.changeFont(font)
        return font

    def openSettingsDialog(self):
        pass

    def cmw_actionConnectToBrkApi(self):
        self.actionConnectToBrkApi.setEnabled(False)
        self.actionDisconnectFromBrkApi.setEnabled(True)
        self.broker.connectToIBKR()

    def cmw_actionDisconnectFromBrkApi(self):
        self.actionConnectToBrkApi.setEnabled(True)
        self.actionDisconnectFromBrkApi.setEnabled(False)
        self.broker.disconnectFromIBKR()

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

        self.actionConnectToBrkApi = QAction(QIcon('icons/Link - 01.png'), 'Connect', self)
        self.actionConnectToBrkApi.setToolTip("Connect toIBKR")
        self.actionConnectToBrkApi.triggered.connect(self.cmw_actionConnectToBrkApi)

        self.actionDisconnectFromBrkApi = QAction(QIcon('icons/Link - 02.png'), 'Disconnect', self)
        self.actionDisconnectFromBrkApi.setToolTip("Disconnect from IBKR")
        self.actionDisconnectFromBrkApi.triggered.connect(self.cmw_actionDisconnectFromBrkApi)

        actionOpenSettings = QAction(QIcon('icons/Gear.png'), 'Disconnect', self)
        actionOpenSettings.setToolTip("Open Settings")
        actionOpenSettings.triggered.connect(self.openSettingsDialog)

        actionClearLiveData = QAction(QIcon('icons/Alpha-Blending.png'), 'ClearLiveData', self)
        actionClearLiveData.setToolTip("Clear Live Data")
        actionClearLiveData.triggered.connect(self.broker.clearLiveData)

        actionUpdateStatusBar = QAction(QIcon('icons/LOL.png'), 'UpdateStatusBar', self)
        actionUpdateStatusBar.setToolTip("Update Statusbar")
        actionUpdateStatusBar.triggered.connect(self.updateStatusBar)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(actionSelectFont)
        toolbar.addAction(actionSelectColor)
        toolbar.addAction(self.actionConnectToBrkApi)
        toolbar.addAction(self.actionDisconnectFromBrkApi)
        toolbar.addAction(actionOpenSettings)
        toolbar.addAction((actionClearLiveData))
        toolbar.addAction((actionUpdateStatusBar))

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Covered Call Analyzer Application')
        self.cmtw.resetAllColumns()


    def closeEvent(self, event):
        print('Calling')
        globvars.ibapp.disconnect()
        print('event: {0}'.format(event))
        event.accept()


