from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Misc.globals import globvars
from .StatusBar import StatusBar
from .ToolBar import ToolBar

import Misc.const
from View.PositionViewer import PositionViewer

class CMainWindow(QMainWindow):
    def __init__(self, w, c, l):
        super().__init__()
        self.settings = QSettings(Misc.const.COMPANY_NAME, Misc.const.APPLICATION_NAME)
        self.centerLayout = QVBoxLayout()

        self.cwidget = w
        self.controller = c
        self.logger = l
        self.positionViewer = PositionViewer(l)

        self.setStatusBar(StatusBar(c))
        self.addToolBar(ToolBar())

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

    def initUI(self):
        self.vspltr = QSplitter(Qt.Vertical)
        self.vspltr.addWidget(self.cwidget)
        self.vspltr.addWidget(self.positionViewer)
        self.setCentralWidget(self.vspltr)
        self.createMenu()


        self.setGeometry(100, 200, 1500, 800)
        self.setWindowTitle('Covered Call Analyzer Application')

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

    def closeEvent(self, event):
        print('Calling')
        self.controller.disconnect()
        print('event: {0}'.format(event))
        event.accept()
