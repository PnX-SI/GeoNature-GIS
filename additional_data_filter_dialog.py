from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import  sys,os

# important pour PyQt5 et gestion du fichier resources.qrc
sys.path.append(os.path.dirname(__file__))
from .resources_rc import *

ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_add_data_filter, _ = uic.loadUiType(os.path.join(ui_path, "additional_data_filter.ui"))



class AddDataFilterWidget(QDialog, form_add_data_filter):

    
    def __init__(self, interface, whost, wport, wbdd, wusername, wpsw, parent=None):
        self.interfaceAddData = interface
        QWidget.__init__(self)
        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        self.pb_loadkeys.clicked.connect(self.loadKeysExemple)

        # self.pb_loadvalues.clicked.connect(self.loadvaluesexemple)


   #---------------------------------------  DEFINITION DES METHODE ---------------------------------------------------------------
        

    def loadKeysExemple(self):

# POUR RÉCUPÉRER LES CLÉS DU CHAMP JSONB : 
#  le champ JSONB se requête comme un dictionnaire 
            # 0 ------------------------------------------------

            db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            db.setHostName(self.host)
            db.setPort(self.port)
            db.setDatabaseName(self.bdd)
            db.setUserName(self.username)
            db.setPassword(self.psw)

            if (not db.open()):
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            else:
                lstkeys = []
                wsql = "SELECT DISTINCT jsonb_object_keys(additional_data) FROM ref_geo.l_areas"
                wsql +="UNION SELECT DISTINCT jsonb_object_keys(additional_data) FROM ref_geo.l_linears"
                wsql +="UNION SELECT DISTINCT jsonb_object_keys(additional_data) FROM ref_geo.l_points"
                wsql +="WHERE additional_data IS NOT NULL;"
                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    while wquery.next():
                        lstkeys.append(wquery.value(0))
                    self.lw_keys.addItems(lstkeys)
    
                db.close()


    # def loadvaluesexemple(self):
