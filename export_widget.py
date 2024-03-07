# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from qgis.core import *
from qgis.gui import *
import sys, os

from .select_export_widget import *
from .filter_widget import *


ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_export, _ = uic.loadUiType(os.path.join(ui_path, "export_dock.ui"))

class ExportWidget(QDockWidget, form_export):
    fermeFenetreFonction = pyqtSignal(list)

    def __init__(self, interface):
        self.interfaceExport = interface
        QWidget.__init__(self)
        self.setupUi(self)


        self.pb_selectview.clicked.connect(self.openSelectExport)


        self.pb_addfilter.clicked.connect(self.openAddFilter)




    def openSelectExport(self):
        connexion = SelectExportWidget(self.interfaceExport)
        connexion.show()
        result = connexion.exec_()
        if result:
            pass

    
    def openAddFilter(self):
        connexion = FilterWidget(self.interfaceExport)
        connexion.show()
        result = connexion.exec_()
        if result:
            pass


    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["export"])
        event.accept()