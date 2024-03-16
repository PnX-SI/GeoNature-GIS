from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import  sys,os

import util_dialog


# important pour PyQt5 et gestion du fichier resources.qrc
sys.path.append(os.path.dirname(__file__))
from .resources_rc import *

ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_add_data_filter, _ = uic.loadUiType(os.path.join(ui_path, "additional_data_filter.ui"))



class AddDataFilterWidget(QDialog, form_add_data_filter):

    
    def __init__(self, interface, whost, wport, wbdd, wusername, wpsw, parent=None):
        self.interfaceAddData = interface
        # QWidget.__init__(self)
        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        self.pb_loadkeys.clicked.connect(self.loadKeysExemple)

        self.lstkeys = []

        self.pb_loadvalues.clicked.connect(self.loadvaluesexemple)

        # self.pb_annuler.clicked.connect(self.cancel)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

   #---------------------------------------  DEFINITION DES METHODE ---------------------------------------------------------------
        

    def loadKeysExemple(self): # 0  EN COURS DE DEV ------------------------------------------------

# POUR RÉCUPÉRER LES CLÉS DU CHAMP JSONB : 
#  le champ JSONB se requête comme un dictionnaire 
           

            db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            db.setHostName(self.host)
            db.setPort(self.port)
            db.setDatabaseName(self.bdd)
            db.setUserName(self.username)
            db.setPassword(self.psw)

            if (not db.open()):
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            else:

                wsql = "SELECT DISTINCT jsonb_object_keys(additional_data) FROM ref_geo.l_areas "
                wsql +="UNION SELECT DISTINCT jsonb_object_keys(additional_data) FROM ref_geo.l_linears "
                wsql +="UNION SELECT DISTINCT jsonb_object_keys(additional_data) FROM ref_geo.l_points "
                wsql +="WHERE additional_data IS NOT NULL; "
                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    QMessageBox.critical(self, u"Impossible de récupérer les clés.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    while wquery.next():
                        print("wquery.value(0) : ", wquery.value(0))
                        print("wquery.value(1) : ", wquery.value(1))
                        self.lstkeys.append(wquery.value(0))
                    self.lw_keys.addItems(self.lstkeys)
    
                db.close()


    def loadvaluesexemple(self): # 0  EN COURS DE DEV ------------------------------------------------
            
# POUR RÉCUPÉRER DES EXEMPLES DE VALEURS DU CHAMP JSONB : 
#  le champ JSONB se requête comme un dictionnaire 
           
            db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            db.setHostName(self.host)
            db.setPort(self.port)
            db.setDatabaseName(self.bdd)
            db.setUserName(self.username)
            db.setPassword(self.psw)

            if (not db.open()):
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            else:
                # for i in self.lstkeys:
                    lstvalues = []
              
                    wsql = "SELECT DISTINCT jsonb_each_text(additional_data) FROM ref_geo.l_areas "
                    wsql +="UNION SELECT DISTINCT jsonb_each_text(additional_data) FROM ref_geo.l_linears "
                    wsql +="UNION SELECT DISTINCT jsonb_each_text(additional_data) FROM ref_geo.l_points "
                    wsql +="WHERE additional_data IS NOT NULL "
                    wsql +="LIMIT 100;"
                    wquery = QSqlQuery(db)
                    wquery.prepare(wsql)
                    if not wquery.exec_():
                        QMessageBox.critical(self, u"Impossible de récupérer les valeurs.", wquery.lastError().text(), QMessageBox.Ok)
                    else:
                        while wquery.next():
                            lstvalues.append(wquery.value(0))
                        self.lw_values.addItems(lstvalues)
        
                    db.close()


    # def cancel(self):
    #     self.reject()

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        QDialog.accept(self)
