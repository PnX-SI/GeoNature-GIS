# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from qgis.core import *
from qgis.gui import *
import sys, os

import util_dialog

from .select_export_dialog import *
from .filter_dialog import *


# important pour PyQt5 et gestion du fichier resources.qrc
sys.path.append(os.path.dirname(__file__))
from .resources_rc import *


ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_export, _ = uic.loadUiType(os.path.join(ui_path, "export_dock.ui"))

class ExportWidget(QDockWidget, form_export):
    fermeFenetreFonction = pyqtSignal(list)

    def __init__(self, interface, whost, wport, wbdd, wusername, wpsw):
        self.interfaceExport = interface
        QDockWidget.__init__(self)
        self.setupUi(self)

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        # Fonction réinitialisation des paramètres des filtes 
        # self.pb_reset.clicked.connect(self.reinitialisation)

        # Fonction pour ouvrir l'aide
        self.pb_help.clicked.connect(util_dialog.openHelp)

        self.pb_selectview.clicked.connect(self.openSelectExport)


        self.pb_addfilter.clicked.connect(self.openAddFilter)

        self.pb_quit.clicked.connect(self.quitter)




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

    def quitter(self):
        self.close()