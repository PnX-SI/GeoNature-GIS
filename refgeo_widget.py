# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.uic import *

from qgis.core import *
from qgis.gui import *
import sys, os


from .additional_data_filter_widget import *
# from .geonaturegisPlugin import *



ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_refgeo, _ = uic.loadUiType(os.path.join(ui_path, "referentiel_geographique_dock.ui"))




class RefGeoWidget(QDockWidget, form_refgeo):
    fermeFenetreFonction = pyqtSignal(list)
    
    

    def __init__(self, interface):

        self.interfaceAddData = interface
        QWidget.__init__(self)
        self.setupUi(self)


        self.pb_additionalFilter.clicked.connect(self.openAddDataFilter)





    def openAddDataFilter(self):
        connexion = AddDataFilterWidget(self.interfaceAddData)
        connexion.show()
        result = connexion.exec_()
        if result:
            pass

    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["refgeo"])
        event.accept()