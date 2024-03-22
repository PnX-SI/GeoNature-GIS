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
    adf_resultat = []
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

        print(typeZone)
        self.getKeys(typeZone)

        self.lw_keys.clicked.connect(self.getValues)
        # Connexion du signal du QPushButton (pb_filtervalue) à la fonction `filtrer_valeurs`
        # self.pb_filtervalue.clicked.connect(self.filtrer_valeurs)
        self.le_filtervalue.textChanged.connect(self.filtrer_valeurs)
        # self.lw_values.itemSelected()
        # self.loadvaluesexemple()
        # self.cb_logical.textActivated.connect()
        # self.cb_keys.textActivated.connect()
        

        # self.cb_operator.textActivated.connect()
        # self.le_selectvalue..connect()
        self.lw_values.itemDoubleClicked.connect(self.valeurVersLineEdit)

        self.pb_add.clicked.connect(self.addQuery)
        self.pb_remove.clicked.connect(self.removeQuery)



        # self.pb_annuler.clicked.connect(self.cancel)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

   #---------------------------------------  DEFINITION DES METHODE ---------------------------------------------------------------
        

    def getKeys(self, typeZone): # 0  EN COURS DE DEV ------------------------------------------------

# POUR RÉCUPÉRER LES CLÉS DU CHAMP JSONB : 
#  le champ JSONB se requête comme un dictionnaire 
            self.adf_resultat = []
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

                wsql = "SELECT DISTINCT  key, value, id_type, nom_table FROM "
                wsql +="(SELECT DISTINCT 'l_areas' as nom_table, (jsonb_each_text(additional_data)).key , (jsonb_each_text(additional_data)).value, id_type FROM ref_geo.l_areas "
                wsql +="UNION SELECT DISTINCT 'l_linears' as nom_table,(jsonb_each_text(additional_data)).key , (jsonb_each_text(additional_data)).value, id_type FROM ref_geo.l_linears "
                wsql +="UNION SELECT DISTINCT 'l_points' as nom_table,(jsonb_each_text(additional_data)).key , (jsonb_each_text(additional_data)).value, id_type FROM ref_geo.l_points) as rq0 "
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
                        if key not in self.dico:
                            self.dico[key] = [value]
                        else:
                            self.dico[key].append(value)

                    if len(self.dico) > 0:
                        for key in self.dico.keys():  
                            self.lw_keys.addItem(str(key))
                    else:
                        QMessageBox.information(self, "Information", "Pas de données additionnelles trouvées ", QMessageBox.Ok)
                  
                db.close()
                self.lw_keys.sortItems(Qt.AscendingOrder)
                
    def getValues(self):
        self.lw_values.clear() 
        selected_key = self.lw_keys.selectedItems()[0].text()
        # print(selected_key)
        # print(selected_key[0].text())
        if selected_key in self.dico:
            
            for value in self.dico[selected_key]: 
                self.lw_values.addItem(value)
        else:
            QMessageBox.information(self, "Information", f"Pas de valeurs trouvées pour : {selected_key}", QMessageBox.Ok)
        self.lw_values.sortItems(Qt.AscendingOrder)
        self.le_selectkey.setText(selected_key)
        

    def filtrer_valeurs(self):
         # Obtenir la valeur du QLineEdit (le_filtervalue)
        valeur_recherche = self.le_filtervalue.text().lower()
        # Filtrer les valeurs de la QListWidget (lw_values)
        if valeur_recherche:
            for i in range(self.lw_values.count()): # On parcour les valeurs de lw_values
                item = self.lw_values.item(i)
                if valeur_recherche in item.text().lower(): # Si dans le text des valeurs de lw_values on identifie la chaine de caractere valeur_recherche
                    item.setHidden(False) # On ne cache pas la valeur
                else:
                    item.setHidden(True) # Sinon on la cache
        else:
            # Si il n'y a pas de valeur_recherche
            for i in range(self.lw_values.count()):
                self.lw_values.item(i).setHidden(False) # on affiche toutes les valeurs
        self.lw_values.sortItems(Qt.AscendingOrder)
  

    def valeurVersLineEdit(self, item):
        self.le_selectvalue.setText(item.text())

    def addQuery(self):

        # Traduction des Arguments Logiques 

        if self.lw_queryresult.count() == 0 : # Si c'est la premiere ligne de requête de la liste on force un "AND"
            logical = " AND "

        else:
            logical = self.cb_logical.currentText()
            if self.cb_logical.currentText() == "ET":
                logical =" AND "
            elif self.cb_logical.currentText() == "OU":
                logical =" OR "

            # print(self.cb_logical.currentText())
            # print(logical)
            
        key = self.le_selectkey.text()
         # if self.cb_operator.currentText() 
        value = self.le_selectvalue.text()

        # Traduction des Opérateurs 
        operator_value = ""

        if self.cb_operator.currentText() == "COMMENCE PAR":
            operator_value =f" ILIKE '{value}%' "
        elif self.cb_operator.currentText() == "CONTIENT":
            operator_value = f" ILIKE '%{value}%' "
        elif self.cb_operator.currentText() == "FINI PAR":
            operator_value = f" ILIKE '%{value}' "
        elif self.cb_operator.currentText() == "PAS EGAL":
            operator_value = f" != {value} "
        elif self.cb_operator.currentText() == "EGAL":
            operator_value = f" = {value} "
        elif self.cb_operator.currentText() == ">":
            operator_value = f" > {value} "
        elif self.cb_operator.currentText() == "<":
            operator_value = f" < {value} "
        elif self.cb_operator.currentText() == ">=":
            operator_value = f" >= {value} "
        elif self.cb_operator.currentText() == "<=":
            operator_value = f" <= {value} "


        # print(self.cb_operator.currentText())
        # print(operator_value)
    
        query = f"{logical} {key} {operator_value}"
        item = QListWidgetItem(query)
        self.lw_queryresult.addItem(item)
         
    def removeQuery(self):
        selected_items = self.lw_queryresult.selectedItems()
        if selected_items:
            for item in selected_items:
                self.lw_queryresult.takeItem(self.lw_queryresult.row(item))

    def reject(self):
        self.lw_keys.clear()
        self.lw_values.clear() 
        self.dico = {}
        self.typeZone = []
        QDialog.reject(self)

    def accept(self):
        for i in range(self.lw_queryresult.count()):
            self.adf_resultat.append(self.lw_queryresult.item(i).text())
        print(self.adf_resultat)
        QDialog.accept(self)
