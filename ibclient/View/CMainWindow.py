from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QLabel, QColorDialog, QFontDialog, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QSettings

from .StatusBar import StatusBar
import Misc.const
from View.PositionViewer import PositionViewer

class CMainWindow(QMainWindow):
    def __init__(self, w, c, l):
        super().__init__()
        self.settings = QSettings(Misc.const.COMPANY_NAME, Misc.const.APPLICATION_NAME)
        self.cwidget = w
        self.controller = c
        self.logger = l
        self.positionViewer = PositionViewer(l)
        self.statusBar = StatusBar(c)

    def initUI(self):
        self.setCentralWidget(self.cwidget)

        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        actionSelectFont = QAction(QIcon('View/icons/Digital - Zero.png'), 'Flee the Scene', self)
        actionSelectFont.setToolTip("Select Font")
        actionSelectFont.triggered.connect(self.openFontDialog)

        actionSelectColor = QAction(QIcon('View/icons/Digital - One.png'), 'Flee the Scene', self)
        actionSelectColor.setToolTip("Select Color")
        actionSelectColor.triggered.connect(self.openColorDialog)

        self.actionConnectToBrkApi = QAction(QIcon('View/icons/Link - 01.png'), 'Connect', self)
        self.actionConnectToBrkApi.setToolTip("Connect toIBKR")
        self.actionConnectToBrkApi.triggered.connect(self.cmw_actionConnectToBrkApi)

        self.actionDisconnectFromBrkApi = QAction(QIcon('View/icons/Link - 02.png'), 'Disconnect', self)
        self.actionDisconnectFromBrkApi.setToolTip("Disconnect from IBKR")
        self.actionDisconnectFromBrkApi.triggered.connect(self.cmw_actionDisconnectFromBrkApi)

        actionOpenSettings = QAction(QIcon('View/icons/Gear.png'), 'Disconnect', self)
        actionOpenSettings.setToolTip("Open Settings")
        actionOpenSettings.triggered.connect(self.openSettingsDialog)

        actionClearLiveData = QAction(QIcon('View/icons/Alpha-Blending.png'), 'ClearLiveData', self)
        actionClearLiveData.setToolTip("Clear Live Data")
        # actionClearLiveData.triggered.connect(self.broker.clearLiveData)

        actionUpdateStatusBar = QAction(QIcon('View/icons/LOL.png'), 'UpdateStatusBar', self)
        actionUpdateStatusBar.setToolTip("Update Statusbar")
        actionUpdateStatusBar.triggered.connect(self.updateStatusBar)

        actionVisualize0 = QAction(QIcon('View/icons/Torch.png'), '', self)
        actionVisualize0.setToolTip("View Position Details")
        actionVisualize0.triggered.connect(self.showPositionViewer)

        self.actionVisualize1 = QAction(QIcon("View/icons/I don't know.png"), '', self)
        self.actionVisualize2 = QAction(QIcon('View/icons/Palm-Tree.png'), '', self)
        self.actionVisualize3 = QAction(QIcon('View/icons/Wand - 01.png'), '', self)
        self.actionVisualize4 = QAction(QIcon('View/icons/Wand - 02.png'), '', self)
        self.actionVisualize5 = QAction(QIcon('View/icons/Tool - Hammer.png'), '', self)
        self.actionVisualize6 = QAction(QIcon('View/icons/Television.png'), '', self)
        self.actionVisualize7 = QAction(QIcon('View/icons/Table-Fan.png'), '', self)
        self.actionVisualize8 = QAction(QIcon('View/icons/Sword-03.png'), '', self)
        self.actionVisualize9 = QAction(QIcon('View/icons/Wine Glass - 01.png'), '', self)

        self.actionVisualize1.setToolTip("")
        self.actionVisualize1.triggered.connect(self.doActionVisualize1)
        self.actionVisualize2.setToolTip("")
        self.actionVisualize2.triggered.connect(self.doActionVisualize2)
        self.actionVisualize3.setToolTip("")
        self.actionVisualize3.triggered.connect(self.doActionVisualize3)
        self.actionVisualize4.setToolTip("")
        self.actionVisualize4.triggered.connect(self.doActionVisualize4)
        self.actionVisualize5.setToolTip("")
        self.actionVisualize5.triggered.connect(self.doActionVisualize5)
        self.actionVisualize6.setToolTip("")
        self.actionVisualize6.triggered.connect(self.doActionVisualize6)
        self.actionVisualize7.setToolTip("")
        self.actionVisualize7.triggered.connect(self.doActionVisualize7)
        self.actionVisualize8.setToolTip("")
        self.actionVisualize8.triggered.connect(self.doActionVisualize8)
        self.actionVisualize9.setToolTip("")
        self.actionVisualize9.triggered.connect(self.doActionVisualize9)

        self.portSelectorCombo = QComboBox()
        self.portSelectorCombo.addItem("TWS REAL  7495")
        self.portSelectorCombo.addItem("TWS PAPER 7497")
        self.portSelectorCombo.addItem("GTW REAL  4001")
        self.portSelectorCombo.addItem("GTW PAPER 4002")
        self.portSelectorCombo.currentIndexChanged.connect(self.changeBrokerPort)

        if (Misc.const.IBPORT == 7495):
            self.portSelectorCombo.setCurrentIndex(0)
        elif (Misc.const.IBPORT == 7497):
            self.portSelectorCombo.setCurrentIndex(1)
        elif (Misc.const.IBPORT == 4001):
            self.portSelectorCombo.setCurrentIndex(2)
        elif (Misc.const.IBPORT == 4002):
            self.portSelectorCombo.setCurrentIndex(3)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(actionSelectFont)
        toolbar.addAction(actionSelectColor)
        toolbar.addWidget(self.portSelectorCombo)
        toolbar.addAction(self.actionConnectToBrkApi)
        toolbar.addAction(self.actionDisconnectFromBrkApi)
        toolbar.addAction(actionOpenSettings)
        toolbar.addAction((actionClearLiveData))
        toolbar.addAction((actionUpdateStatusBar))
        toolbar.addAction(actionVisualize0)
        toolbar.addAction(self.actionVisualize1)
        toolbar.addAction(self.actionVisualize2)
        toolbar.addAction(self.actionVisualize3)
        toolbar.addAction(self.actionVisualize4)
        toolbar.addAction(self.actionVisualize5)
        toolbar.addAction(self.actionVisualize6)
        toolbar.addAction(self.actionVisualize7)
        toolbar.addAction(self.actionVisualize8)
        toolbar.addAction(self.actionVisualize9)

        self.setStatusBar(self.statusBar)

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Covered Call Analyzer Application')

    def doActionVisualize1(self):
        pass

    def doActionVisualize0(self):
        pass

    def doActionVisualize2(self):
        cc = self.cwidget.getSelectedRow()
        if cc != None:
            self.controller.getStockData(cc)
        self.positionViewer.updateMplChart(cc)

    def doActionVisualize3(self):
        pass
    def doActionVisualize4(self):
        pass
    def doActionVisualize5(self):
        pass
    def doActionVisualize6(self):
        pass
    def doActionVisualize7(self):
        pass
    def doActionVisualize8(self):
        pass
    def doActionVisualize9(self):
        pass

    def changeBrokerPort(self):
        port = 4002
        if self.portSelectorCombo.currentText() == "TWS REAL  7495":
            port= 7495
        if self.portSelectorCombo.currentText() == "TWS PAPER 7497":
            port= 7497
        if self.portSelectorCombo.currentText() == "GTW REAL  4001":
            port= 4001
        if self.portSelectorCombo.currentText() == "GTW PAPER 4002":
            port= 4002

        self.controller.changeBrokerPort(port)

    def showPositionViewer(self):
        self.positionViewer.show()

    def updateStatusBar(self):
            self.statusBar.update()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        tauAct = cmenu.addAction("toggleAutoUpdate")
        openAct = cmenu.addAction("Show All Columns")
        resetColumnState = cmenu.addAction("Reset Columns")
        clearSelection = cmenu.addAction("Clear Selection")

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == tauAct:
            self.controller.toggleAutoUpdate()
        elif action == openAct:
            self.controller.showAllColumns()
        elif action == resetColumnState:
            self.controller.resetAllColumns()
        elif action == clearSelection:
            self.controller.clearSelection()

    def openColorDialog(self):
        c = QColorDialog.getColor()
        return c

    def openFontDialog(self):
        (font,ok) = QFontDialog.getFont()
        print(str(font))
        if ok:
            self.cwidget.changeFont(font)
        return font

    def openSettingsDialog(self):

        pass

    def cmw_actionConnectToBrkApi(self):
        self.actionConnectToBrkApi.setEnabled(False)
        self.actionDisconnectFromBrkApi.setEnabled(True)
        self.controller.connect()

    def cmw_actionDisconnectFromBrkApi(self):
        self.actionConnectToBrkApi.setEnabled(True)
        self.actionDisconnectFromBrkApi.setEnabled(False)
        self.controller.disconnect()

    def closeEvent(self, event):
        print('Calling')
        self.controller.disconnect()
        print('event: {0}'.format(event))
        event.accept()
