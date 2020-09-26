from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QLabel, QColorDialog, QFontDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from .StatusBar import StatusBar

class CMainWindow(QMainWindow):
    def __init__(self, w, c ):
        super().__init__()

        self.cwidget = w
        self.controller = c

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

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(actionSelectFont)
        toolbar.addAction(actionSelectColor)
        toolbar.addAction(self.actionConnectToBrkApi)
        toolbar.addAction(self.actionDisconnectFromBrkApi)
        toolbar.addAction(actionOpenSettings)
        toolbar.addAction((actionClearLiveData))
        toolbar.addAction((actionUpdateStatusBar))

        self.setStatusBar(self.statusBar)

        self.setGeometry(100, 200, 1500, 500)
        self.setWindowTitle('Covered Call Analyzer Application')

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

    def startUpdateTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStatusBar)
        self.timer.start(1000)
        self.controller.startModelTimer()

    def closeEvent(self, event):
        print('Calling')
        self.controller.disconnect()
        print('event: {0}'.format(event))
        event.accept()
