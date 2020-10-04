import logging
from Misc.globals import globvars

def initMainLogger():
    mainLogger = logging.getLogger(__name__)
    mainLogger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(globvars.logfilename, mode='a')

    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    mainLogger.addHandler(fileHandler)
    mainLogger.propagate = True
    return mainLogger

def initApiLogger():
    apiLogger = logging.getLogger(__name__)
    apiLogger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(globvars.apilogfilename, mode='a')

    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    apiLogger.addHandler(fileHandler)
    apiLogger.propagate = True
    return apiLogger

