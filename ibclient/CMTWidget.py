from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

from CMTModel import CMTModel, PrxyModel
from globals import globvars
import const

class CMTWidget(QWidget):
    def __init__(self, dataList, header, ccd, *args):
        QWidget.__init__(self, *args)
        self.autoUpdate = True
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on the header to sort table")

        self.table_model = CMTModel(self, dataList, header)

        self.proxy_model = PrxyModel()
        self.proxy_model.setSourceModel(self.table_model)

        self.table_model.setCCList(ccd)
        self.table_view = QTableView()

        self.table_view.setFont(QFont("Times", 11));

        # self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        # bind cell click to a method reference
        self.table_view.clicked.connect(self.showSelection)
        self.table_view.clicked.connect(self.selectRow)

        self.table_view.setModel(self.proxy_model)
        # enable sorting
        self.table_view.setSortingEnabled(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def toggleAutoUpdate(self):
        if self.autoUpdate == True:
            self.autoUpdate = False
        else:
            self.autoUpdate = True

        self.table_model.setAutoUpdate(self.autoUpdate)

    def update_model(self, datalist, header):
        self.table_model2 = MyTableModel(self, dataList, header)
        self.table_view.setModel(self.table_model2)
        self.table_view.update()

    def showSelection(self, item):
        cellContent = item.data()
        # print(cellContent)  # test
        sf = "You clicked on {}".format(cellContent)
        # display in title bar for convenience
        self.setWindowTitle(sf)

    def selectRow(self, index):
        # print("current row is %d", index.row())
        pass
