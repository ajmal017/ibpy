import Model
from Misc.globals import globvars

class Controller:
    def __init__(self, model):
        self.model = model
        self.autoUpdate = True

    def initData(self,v):
        self.view = v

    def getStockData(self, cc):
        self.model.getHistStockData(cc)
        pass

    def getNumPositions(self):
        return self.model.getNumPositions()

    def connect(self):
        self.model.connectBroker()

    def disconnect(self):
        self.model.disconnectBroker()

    def changeBrokerPort(self, port):
        self.model.changeBrokerPort(port)

    def toggleAutoUpdate(self):
        if self.autoUpdate == True:
            self.autoUpdate = False
        else:
            self.autoUpdate = True

        self.model.setAutoUpdate(self.autoUpdate)

    def resetAllColumns(self):
        self.view.resetAllColumns()

    def showAllColumns(self):
        l = self.model.columnCount(None)
        self.view.showAllColumns(l)

    def clearSelection(self):
        self.view.clearSelection()
