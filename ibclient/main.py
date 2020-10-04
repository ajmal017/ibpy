from PyQt5.QtWidgets import *

from View.CMainWindow import CMainWindow
from View.CMTWidget import CMTWidget
from Controller.CMTController import  Controller
from Model.CMTModel import CMTModel
from Logs import logger as logger
from Misc.globals import globvars

if __name__ == '__main__':
    globvars.init_globvars()
    capp = QApplication([])

    mainLogger = logger.initMainLogger()
    globvars.set_logger(mainLogger)
    globvars.logger.info("**********************************************")
    globvars.logger.info("*          IBPY - Covered Call Analyzer      *")
    globvars.logger.info("**********************************************")

    model = CMTModel()
    controller = Controller(model)
    model.initData(controller)

    view = CMTWidget(model)
    cmw = CMainWindow(view, controller, mainLogger)
    controller.initData(view)

    cmw.initUI()
    cmw.show()
    controller.resetAllColumns()
    capp.exec_()
