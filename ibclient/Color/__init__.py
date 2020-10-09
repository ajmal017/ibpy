import tkinter as tk

MAX_ROWS = 36
FONT_SIZE = 15  # (pixels)
from .colorpalette import PALETTES_NAMED, hex2rgb, rgb2hex
#from .ColorDemo import open_color_demo


__local__ = ['PALETTES_NAMED', 'open_color_demo', 'hex2rgb', 'rgb2hex']

__external__ = ['tk', 'globvars', 'MAX_ROWS', 'FONT_SIZE']

__all__ = __external__ + __local__
