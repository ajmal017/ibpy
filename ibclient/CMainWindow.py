import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMenu, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from CMTWidget import CMTWidget
from globals import globvars


class CMainWindow(QMainWindow):
    def __init__(self, dataList, header, ccd):
        super().__init__()

        self.statusbar = self.statusBar()
        self.setStatusBar(self.statusbar)

        #self.statusbar.showMessage('Ready')

        self.nlv_lbl = QLabel("NLV in USD:"+"0")
        #self.statusbar.addWidget(self.nlv_lbl)
        self.statusBar().addPermanentWidget(self.nlv_lbl)
        self.nlv_lbl.show()

        self.dataList = dataList
        self.header = header
        self.initUI(ccd)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStatusBar)
        self.timer.start(1000)

    def updateStatusBar(self):
        print("update statusbar ", globvars.accountData["NetLiquidationByCurrency"][0])
        self.nlv_lbl.text = globvars.accountData["NetLiquidationByCurrency"][0]

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        tauAct = cmenu.addAction("toggleAutoUpdate")
        openAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == tauAct:
            self.cmtw.toggleAutoUpdate()

    def initUI(self, ccd):

        self.cmtw = CMTWidget(self.dataList, self.header, ccd)
        self.setCentralWidget(self.cmtw)

        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Main window')
        self.show()
