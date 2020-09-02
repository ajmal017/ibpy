import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMenu
from PyQt5.QtGui import QIcon


from CMTWidget import CMTWidget

class CMainWindow(QMainWindow):
    def __init__(self, dataList, header, ccd):
        super().__init__()

        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.dataList = dataList
        self.header = header
        self.initUI(ccd)

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
