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

        self.cwidget    = w
        self.controller = c
        self.logger     = l
        self.positionViewer = PositionViewer(l)
        self.cwidget.setPositionViewer(self.positionViewer)
        self.statusBar = StatusBar(self,c)
        self.setStatusBar(self.statusBar)
        self.addToolBar(ToolBar(w,c,self.positionViewer))

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
        self.centerLayout = QVBoxLayout()

        self.dock2 = QDockWidget("Portfolio Table: "+str(self.controller.getNumPositions()) + " Positions")
        self.dock2.setAllowedAreas(Qt.TopDockWidgetArea)
        self.dock2.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dock2.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dock2.setAllowedAreas(Qt.RightDockWidgetArea)
        self.dock2.setObjectName("Table")
        self.dock2.DockWidgetVerticalTitleBar
        self.dock2.setWidget(self.cwidget)
        # self.dock2.topLevelChanged.connect(lambda: self.dock2.setWindowFlags(Qt.CustomizeWindowHint|Qt.Window|Qt.WindowMaximizeButtonHint|Qt.WindowMinimizeButtonHint))

        #
        # # ticon = self.dock2.style().standardIcon(QStyle.SP_TitleBarMaxButton)
        # # # ticon = self.dock2.style().standardIcon(QStyle.SP_TitleBarMaxButton, 0, self.dock2);
        # self.titlebar = QWidget()
        # titlebarLayout = QHBoxLayout()
        # self.titlebar.setLayout(titlebarLayout)
        # # ttlbtn = QPushButton(icon=ticon)
        # ttlbtn = QPushButton()
        # titlebarLayout.addWidget(ttlbtn)
        # self.dock2.setTitleBarWidget(self.titlebar)

        self.dock1 = QDockWidget("Single Position Chart")
        self.dock1.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dock1.setAllowedAreas(Qt.TopDockWidgetArea)
        self.dock1.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dock1.setAllowedAreas(Qt.RightDockWidgetArea)
        self.dock1.setObjectName("PositionChart")
        self.dock1.setWidget(self.positionViewer)
        # self.dock1.topLevelChanged.connect(lambda: self.dock1.setWindowFlags(Qt.CustomizeWindowHint|Qt.Window|Qt.WindowMaximizeButtonHint|Qt.WindowMinimizeButtonHint))

        self.centerLayout.addWidget(self.dock2)
        self.centerLayout.addWidget(self.dock1)

        centralWidget = QWidget()
        centralWidget.setLayout(self.centerLayout)
        self.setCentralWidget(centralWidget)
        self.createMenu()

        self.setGeometry(50, 50, 1500, 800)

    def updateWindowTitle(self,val):
        self.setWindowTitle(val+"Covered Call Analyzer Application: NLQ=")

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
