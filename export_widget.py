# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from qgis.core import *
from qgis.gui import *
import sys, os


ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_export, _ = uic.loadUiType(os.path.join(ui_path, "export_dock.ui"))

class ExportWidget(QDockWidget, form_export):
    fermeFenetreFonction = pyqtSignal(list)

    def __init__(self, interface):
        QWidget.__init__(self)
        self.setupUi(self)

    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["Export"])
        event.accept()