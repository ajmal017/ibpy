import os
from pyshortcuts import make_shortcut

make_shortcut(os.path.join(os.getcwd(),"main.ps1"), name='MYCOVCALLANALYZER', icon='./View/icons/Dollar-Coin', executable="powershell")
