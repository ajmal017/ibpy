from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

from CMTModel import CMTModel, PrxyModel
from globals import globvars
import const
from covcall import covered_call

class CMTWidget(QWidget):
    def __init__(self, dataList, ccd, *args):
        QWidget.__init__(self, *args)
        self.autoUpdate = True
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on the header to sort table")

        self.table_model = CMTModel(self, dataList)

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

        self.columnsHidden = covered_call.columns_hidden()

        self.resetAllColumns()


        header = self.table_view.horizontalHeader();
        header.sectionDoubleClicked.connect(self.onSectionDoubleClicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def onSectionDoubleClicked(self, logicalIndex):
        self.table_view.hideColumn(logicalIndex)
        print("onSectionDoubleClicked:", logicalIndex)

    def showAllColumns (self):
        l = self.table_model.columnCount(None)
        for col in range(l):
            self.table_view.showColumn(col)

    def resetAllColumns(self):
        for ci, col in enumerate(self.columnsHidden):
            if col == True:
                self.table_view.hideColumn((ci))

    def clearSelection(self):
        self.table_view.clearSelection()

    def toggleAutoUpdate(self):
        if self.autoUpdate == True:
            self.autoUpdate = False
        else:
            self.autoUpdate = True

        self.table_model.setAutoUpdate(self.autoUpdate)

    def showSelection(self, item):
        cellContent = item.data()
        # print(cellContent)  # test
        sf = "You clicked on {}".format(cellContent)
        # display in title bar for convenience
        self.setWindowTitle(sf)

    def selectRow(self, index):
        # print("current row is %d", index.row())
        pass
