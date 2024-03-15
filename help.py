from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import sys, os  



def openHelp(self):
    localHelp = (os.path.dirname(__file__) + "/help/user_manual_FR.pdf")
    localHelp = localHelp.replace("\\","/")
    QDesktopServices.openUrl(QUrl(localHelp))