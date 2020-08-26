#!python3
from tkinter import Tk
import util.const as const
import argparse
import time
import datetime
import logger as logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="", usage='Mandatory parameter missing')
    parser.add_argument('-t', '--test'       , help="test arg: \"test1\" or \"test2\"",default="test2")

    args = parser.parse_args()
    testarg     = args.test.lower()

    root = Tk()
    root.geometry("600x250")

    app = GuiMainFrame(root, parameter)