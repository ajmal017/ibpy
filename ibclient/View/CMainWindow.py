from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QLabel, QColorDialog, QFontDialog, QComboBox
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import QTimer, QSettings

from Misc.globals import globvars
from .StatusBar import StatusBar
import Misc.const
from View.PositionViewer import PositionViewer
from Color import PALETTES_NAMED

class CMainWindow(QMainWindow):
    def __init__(self, w, c, l):
        super().__init__()
        self.settings = QSettings(Misc.const.COMPANY_NAME, Misc.const.APPLICATION_NAME)
        self.centerLayout = QVBoxLayout()

        self.cwidget = w
        self.controller = c
        self.logger = l
        self.positionViewer = PositionViewer(l)
        self.statusBar = StatusBar(c)

        self.centerLayout.addWidget(self.cwidget)
        self.centerLayout.addWidget(self.positionViewer)

    def createMenu(self):
        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        return menubar

    def addAction(self, icon, tttext, callback):
        action = QAction(QIcon(icon), 'Flee the Scene', self)
        action.setToolTip(tttext)
        action.triggered.connect(callback)
        return action

    def initUI(self):
        self.vspltr = QSplitter(Qt.Vertical)
        self.vspltr.addWidget(self.cwidget)
        self.vspltr.addWidget(self.positionViewer)
        self.setCentralWidget(self.vspltr)
        self.createMenu()

        actionSelectFont                    = self.addAction('View/icons/Digital - Zero.png', "Select Font", self.openFontDialog)
        self.actionConnectToBrkApi          = self.addAction('View/icons/Link - 01.png', "Connect toIBKR", self.cmw_actionConnectToBrkApi)
        self.actionDisconnectFromBrkApi     = self.addAction('View/icons/Link - 02.png', "Disconnect from IBKR", self.cmw_actionDisconnectFromBrkApi)
        actionShowPositionViewer            = self.addAction('View/icons/Torch.png', "Show Position", self.showPositionViewer)
        self.actionResizeColumnWidth = self.addAction("View/icons/I don't know.png", "resize columnwidth in table", self.doActionResizeColumns)

        self.colorSelectorCombo = QComboBox()
        for k in PALETTES_NAMED:
            self.colorSelectorCombo.addItem(k)

        self.colorSelectorCombo.setCurrentIndex(1)
        self.colorSelectorCombo.currentIndexChanged.connect(self.changeColorPalette)

        self.watchlistSelectorCombo = QComboBox()
        self.watchlistSelectorCombo.addItem("Current Portfolio")
        self.watchlistSelectorCombo.addItem("BCI Candidates")
        self.watchlistSelectorCombo.addItem("Closed Positions")

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
        toolbar.addAction(actionShowPositionViewer)
        toolbar.addAction(self.actionResizeColumnWidth)
        toolbar.addSeparator()
        toolbar.addWidget(self.colorSelectorCombo)
        toolbar.addSeparator()
        toolbar.addWidget(self.watchlistSelectorCombo)
        toolbar.addSeparator()
        toolbar.addWidget(self.portSelectorCombo)
        toolbar.addAction(self.actionConnectToBrkApi)
        toolbar.addAction(self.actionDisconnectFromBrkApi)

        self.setStatusBar(self.statusBar)

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Covered Call Analyzer Application')

    def doActionResizeColumns(self):
        self.cwidget.table_view.resizeColumnsToContents();

    def showPositionViewer(self):
        cc = self.cwidget.getSelectedRow()
        if cc != None:
            self.controller.getStockData(cc)
            self.positionViewer.updateMplChart(cc)

    def changeColorPalette(self):
        globvars.colors = PALETTES_NAMED[self.colorSelectorCombo.currentText()]

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

    def openFontDialog(self):
        font, ok = QFontDialog.getFont(self.cwidget.current_font)
        print(str(font))
        if ok:
            self.cwidget.changeFont(font)
        return font

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
