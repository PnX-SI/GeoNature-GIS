from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import os


ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_connect, _ = uic.loadUiType(os.path.join(ui_path, "connect.ui"))




class ConnexionWidget(QDialog, form_connect):
    def __init__(self, interface):
        
        QWidget.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets



















# class ConnexionWidget(QWidget, form_connect):
    
    # def __init__(self, parent=None):
    #     super(ConnexionWidget, self).__init__(parent)

    #     save = QSettings()

    #     #champs de connexion à la base de données
    #     self.db = QSqlDatabase.addDatabase("Geonature", "geonature")
    #     self.db.setHostName(QLineEdit, "le_host")
    #     self.db.setPort(int(QLineEdit, "le_port"))
    #     self.db.setDatabaseName(QLineEdit, "le_bdd")


    #     #champs authentification
    #     self.db.setUserName(QLineEdit, "le_username")
    #     self.db.setPassword(QgsPasswordLineEdit, "le_psw")

    #     if (not self.db.open()):
    #         # apparition d'un message d'erreur si la connexion a la base ne s'effectue pas
    #         QMessageBox.critical(self, "Erreur", u"Impossible de se connecter à la base de données ...", QMessageBox.Ok)
    #     else:
    #         print("c'est good !")