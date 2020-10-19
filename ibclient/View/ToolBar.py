from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QMenu, QLabel, QColorDialog, QFontDialog, QComboBox
from PyQt5.QtGui import QIcon

from Misc.globals import globvars
import Misc.const
from Color import PALETTES_NAMED

class ToolBar(QToolBar):
    def __init__(self, w, c, p, parent = None):
        super(ToolBar, self).__init__(parent)
        self.cwidget = w
        self.controller = c
        self.positionViewer = p
        self.actionSelectFont               = self.myAddAction('View/icons/Digital - Zero.png', "Select Font"                 , self.openFontDialog)
        self.actionShowPositionViewer       = self.myAddAction('View/icons/Torch.png', "Show Position"                        , self.showPositionViewer)
        self.actionResizeColumnWidth        = self.myAddAction("View/icons/I don't know.png", "resize columnwidth in table"   , self.doActionResizeColumns)
        self.actionUpdateHistory = self.myAddAction('View/icons/Signal.png', "Update Historydata", self.updateHistory)
        self.addSeparator()
        self.colorSelectorCombo             = self.getColorCbx()
        self.addWidget(self.colorSelectorCombo)
        self.addSeparator()
        self.watchlistSelectorCombo         = self.getWatchlistCbx()
        self.addWidget(self.watchlistSelectorCombo)
        self.addSeparator()
        self.portSelectorCombo              = self.getPortSelectlistCbx()
        self.addWidget(self.portSelectorCombo)
        self.actionConnectToBrkApi          = self.myAddAction('View/icons/Link - 01.png', "Connect toIBKR"                   , self.cmw_actionConnectToBrkApi)
        self.actionDisconnectFromBrkApi     = self.myAddAction('View/icons/Link - 02.png', "Disconnect from IBKR"             , self.cmw_actionDisconnectFromBrkApi)
        self.portSelectorCombo.currentIndexChanged.connect(self.changeBrokerPort)
        self.filterSelectorCombo              = self.getFilterSelectCbx()
        self.candleWidthSelectorCombo              = self.getCandleWidthSelectCbx()

        self.filterSelectorCombo.currentIndexChanged.connect(self.changeFilter)
        self.filterSelectorCombo.setCurrentIndex(0)
        self.candleWidthSelectorCombo.currentIndexChanged.connect(self.changeCandleWidth)
        self.candleWidthSelectorCombo.setCurrentIndex(2)
        self.addWidget(self.filterSelectorCombo)
        self.addWidget(self.candleWidthSelectorCombo)

    def myAddAction(self, icon, tttext, callback):
        action = QAction(QIcon(icon), 'Flee the Scene', self)
        action.setToolTip(tttext)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def getColorCbx(self):
        ret = QComboBox()
        for k in PALETTES_NAMED:
            ret.addItem(k)
        ret.setCurrentIndex(1)
        ret.currentIndexChanged.connect(self.changeColorPalette)
        return ret

    def getWatchlistCbx(self):
        ret = QComboBox()
        ret.addItem("Current Portfolio")
        ret.addItem("BCI Candidates")
        ret.addItem("Closed Positions")
        return ret

    def getCandleWidthSelectCbx(self):
        ret = QComboBox()
        ret.addItem("1 min")
        ret.addItem("5 min")
        ret.addItem("60 min")
        return ret

    def getFilterSelectCbx(self):
        ret = QComboBox()
        ret.addItem("include closed positions")
        ret.addItem("excluse closed positions")
        return ret


    def getPortSelectlistCbx(self):
        ret = QComboBox()
        ret.addItem("TWS REAL  7495")
        ret.addItem("TWS PAPER 7497")
        ret.addItem("GTW REAL  4001")
        ret.addItem("GTW PAPER 4002")
        if (Misc.const.IBPORT == 7495):
            ret.setCurrentIndex(0)
        elif (Misc.const.IBPORT == 7497):
            ret.setCurrentIndex(1)
        elif (Misc.const.IBPORT == 4001):
            ret.setCurrentIndex(2)
        elif (Misc.const.IBPORT == 4002):
            ret.setCurrentIndex(3)
        return ret

    def doActionResizeColumns(self):
        self.cwidget.table_view.resizeColumnsToContents();

    def showPositionViewer(self):
        cc = self.cwidget.getSelectedRow()
        if cc != None:
            if self.controller.getStockData(cc):
                self.positionViewer.updateMplChart(cc)

    def changeColorPalette(self):
        globvars.colors = PALETTES_NAMED[self.colorSelectorCombo.currentText()]

    def changeCandleWidth(self):
        curCandleWidthText = self.candleWidthSelectorCombo.currentText()
        if curCandleWidthText == "1 min":
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH1
        elif curCandleWidthText == "5 min":
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH5
        elif curCandleWidthText == "60 min":
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH60


    def changeFilter(self):
        curtext = self.filterSelectorCombo.currentText()
        if curtext == "include closed positions":
            self.controller.model.includeZeroPositions = True
        else:
            self.controller.model.includeZeroPositions = False

    def changeCandleWidth(self):
        curtext = self.candleWidthSelectorCombo.currentText()
        if curtext == "1 min":
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH1
        elif curtext == "5 min":
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH5
        elif curtext == "60 min":
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH60
        else:
            self.controller.model.candleWidth = Misc.const.CANDLEWIDTH5

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

    def openFontDialog(self):
        font, ok = QFontDialog.getFont(self.cwidget.current_font)
        print(str(font))
        if ok:
            self.cwidget.changeFont(font)
        return font

    def updateHistory(self):
        self.controller.updateHistory()

    def cmw_actionConnectToBrkApi(self):
        self.actionConnectToBrkApi.setEnabled(False)
        self.actionDisconnectFromBrkApi.setEnabled(True)
        self.controller.connect()

    def cmw_actionDisconnectFromBrkApi(self):
        self.actionConnectToBrkApi.setEnabled(True)
        self.actionDisconnectFromBrkApi.setEnabled(False)
        self.controller.disconnect()
