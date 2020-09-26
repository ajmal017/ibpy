import Model


class Controller:
    def __init__(self, model):
        self.model = model
        self.autoUpdate = True

    def initData(self,v):
        self.view = v

    def connect(self):
        self.model.connectBroker()

    def disconnect(self):
        self.model.disconnectBroker()

    def toggleAutoUpdate(self):
        if self.autoUpdate == True:
            self.autoUpdate = False
        else:
            self.autoUpdate = True

        self.model.setAutoUpdate(self.autoUpdate)

    def startModelTimer(self):
        self.model.startModelTimer()

    def resetAllColumns(self):
        self.view.resetAllColumns()

    def showAllColumns(self):
        l = self.model.columnCount(None)
        self.view.showAllColumns(l)

    def clearSelection(self):
        self.view.clearSelection()
