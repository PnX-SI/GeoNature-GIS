# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os

def openHelp(self):
    localHelp = (os.path.dirname(__file__) + "/help/user_manual_FR.pdf")
    localHelp = localHelp.replace("\\","/")
    QDesktopServices.openUrl(QUrl.fromLocalFile(localHelp))
    print(localHelp)