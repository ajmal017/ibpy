from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Model.CMTModel import CMTModel, PrxyModel
from Controller.covcall import covered_call

class CMTWidget(QWidget):
    def __init__(self, model, *args):
        QWidget.__init__(self, *args)
        pal = QPalette()

        self.autoUpdate = True
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle("Click on the header to sort table")

        self.table_view = QTableView()
        self.proxy_model = PrxyModel()

        self.table_model = model
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)

        self.table_view.setPalette(pal)

        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.table_view.clicked.connect(self.showSelection)
        self.table_view.clicked.connect(self.selectRow)

        # enable sorting
        self.table_view.setSortingEnabled(True)

        self.table_view.horizontalHeader().sectionDoubleClicked.connect(self.onSectionDoubleClicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        # ft = QFont("MS Shell Dlg 2", 8, QFont.Bold)
        ft = QFont("Courier New", 7, QFont.Bold)
        self.table_view.setFont(ft);
        self.setLayout(layout)
        self.table_view.resizeColumnsToContents();

    def changeFont(self, font):
         #ft = QFont("Times", 12, QFont.Bold)
        self.table_view.setFont(font)
        self.table_view.resizeColumnsToContents()
        self.table_view.update()

    def onSectionDoubleClicked(self, logicalIndex):
        self.table_view.hideColumn(logicalIndex)
        print("onSectionDoubleClicked:", logicalIndex)

    def resetAllColumns(self):
        for ci, col in enumerate(covered_call.columns_hidden()):
            if col == True:
                self.table_view.hideColumn((ci))

    def showAllColumns (self, l):
        for col in range(l):
            self.table_view.showColumn(col)

    def clearSelection(self):
        self.table_view.clearSelection()

    def showSelection(self, item):
        cellContent = item.data()
        # print(cellContent)  # test
        sf = "You clicked on {}".format(cellContent)
        # display in title bar for convenience
        self.setWindowTitle(sf)

    def selectRow(self, index):
        # print("current row is %d", index.row())
        pass
