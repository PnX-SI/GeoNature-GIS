from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import  sys,os
# import json 

import util_dialog
# import refgeo_dialog

# important pour PyQt5 et gestion du fichier resources.qrc
sys.path.append(os.path.dirname(__file__))
from .resources_rc import *

ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_add_data_filter, _ = uic.loadUiType(os.path.join(ui_path, "additional_data_filter.ui"))



class AddDataFilterWidget(QDialog, form_add_data_filter):

    dico = {} 
    def __init__(self, interface, whost, wport, wbdd, wusername, wpsw, typeZone, parent=None):
        self.interfaceFenetres = interface
        # QWidget.__init__(self)
        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        
        self.getKeys(typeZone)

        self.lw_keys.itemDoubleClicked.connect(self.getValues)
        # self.lw_values.itemSelected()
        # self.loadvaluesexemple()
        # self.cb_logical.textActivated.connect()
        # self.cb_keys.textActivated.connect()
        # self.cb_operator.textActivated.connect()
        # self.le_selectvalue.textChanged.connect()
        # self.pb_add.clicked.connect()
        # self.pb_remove.clicked.connect()

        # self.pb_annuler.clicked.connect(self.cancel)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

   #---------------------------------------  DEFINITION DES METHODE ---------------------------------------------------------------
        

    def getKeys(self, typeZone): # 0  EN COURS DE DEV ------------------------------------------------

# POUR RÉCUPÉRER LES CLÉS DU CHAMP JSONB : 
#  le champ JSONB se requête comme un dictionnaire 
            self.lw_keys.clear()
            self.dico.clear
            
            db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            db.setHostName(self.host)
            db.setPort(self.port)
            db.setDatabaseName(self.bdd)
            db.setUserName(self.username)
            db.setPassword(self.psw)

            if (not db.open()):
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            else:

                wsql = "SELECT DISTINCT key, value, id_type FROM "
                wsql +="(SELECT DISTINCT (jsonb_each_text(additional_data)).key , (jsonb_each_text(additional_data)).value, id_type FROM ref_geo.l_areas "
                wsql +="UNION SELECT DISTINCT (jsonb_each_text(additional_data)).key , (jsonb_each_text(additional_data)).value, id_type FROM ref_geo.l_linears "
                wsql +="UNION SELECT DISTINCT (jsonb_each_text(additional_data)).key , (jsonb_each_text(additional_data)).value, id_type FROM ref_geo.l_points) as rq0 "
                wsql +="WHERE key IS NOT NULL AND value IS NOT NULL AND id_type IN (" + ", ".join(typeZone)  + "); "
                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    QMessageBox.critical(self, u"Impossible de récupérer les clés.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    
                    while wquery.next():
                        # print("wquery.value(0) : ", wquery.value(0))
                        # print("wquery.value(1) : ", wquery.value(1))                                       
                        key = (wquery.value(0))
                        value = (wquery.value(1))
                        # if key not in self.dico:
                        #      self.dico[key] = value
                        self.dico[key] = value
                    if len(self.dico) > 0:
                        for key in self.dico.keys():  
                            self.lw_keys.addItem(str(key))
                    else:
                        QMessageBox.information(self, "Information", f"Pas de clés trouvées", QMessageBox.Ok)
                        # self.lw_keys.addItem("Pas de clés trouvées pour ce type de zonage")                    
                db.close()
                print(wsql)
                print(len(self.dico))
                print(typeZone) #pour débug
                
    def getValues(self):
        self.lw_values.clear() 
        selected_key = self.lw_keys.selectedItems()[0]
        if selected_key in self.dico:
            
            for value in self.dico[selected_key]: 
                self.lw_values.addItem(value)
        else:
            QMessageBox.information(self, "Information", f"Pas de valeurs trouvées : {selected_key}", QMessageBox.Ok)

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

    # def filterconstructor(self):
        #  selectlogical = 
        #  selectkey = 
        #  selectoperator = 


    def reject(self):
        self.lw_keys.clear()
        self.lw_values.clear() 
        self.dico = {}
        self.typeZone = []
        QDialog.reject(self)

    def accept(self):
        QDialog.accept(self)
