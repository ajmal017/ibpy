import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMenu, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from CMTWidget import CMTWidget
from globals import globvars

class CMainWindow(QMainWindow):
    def __init__(self, dataList):
        super().__init__()

        self.statusbar = self.statusBar()
        self.setStatusBar(self.statusbar)
        self.dataList = dataList

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStatusBar)
        self.timer.start(1000)

    def updateStatusBar(self):
        profstr = "NLQ: "
        profstr += globvars.accountData["NetLiquidation"] + " CHF | "

        for cncid,cnc in enumerate(globvars.accountData["NetLiquidationByCurrency"]):
            try:
                profstr += cnc + " | "
                profstr += " "
            except:
                pass

        profstr += " TVP: ALL "
        profstr += "{:.2f}".format(globvars.tvprofit)

        profstr += " InitMargin "
        profstr += globvars.accountData["FullInitMarginReq"]

        self.statusbar.showMessage(profstr)

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

    def initUI(self, ccd):

        self.cmtw = CMTWidget(self.dataList, ccd)
        self.setCentralWidget(self.cmtw)

        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Main window')

    def closeEvent(self, event):
        print('Calling')
        globvars.ibapp.disconnect()
        print('event: {0}'.format(event))
        event.accept()


