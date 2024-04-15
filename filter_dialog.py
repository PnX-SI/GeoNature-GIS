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
form_connect, _ = uic.loadUiType(os.path.join(ui_path, "filter.ui"))

#---------000000 EN COURS DE DEV 000000-----------------------------


class FilterWidget(QDialog, form_connect):

    def __init__(self, interfaceFenetres, whost, wport, wbdd, wusername, wpsw, selected_view_schema, selected_view_name, parent=None):
        self.interfaceFenetres = interfaceFenetres

        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        self.filter_result =[]
        self.schema = selected_view_schema[0]
        self.vue = selected_view_name[0]
        self.dico = {}
        self.dico_fields_name_type = {}

        self.lw_fields.clicked.connect(self.getValues)

        # Connexion du signal du QPushButton (pb_filtervalue) à la fonction `filtrer_valeurs`
        self.le_filtervalue.textChanged.connect(self.filtrer_valeurs)

        self.lw_values.itemDoubleClicked.connect(self.valeurVersLineEdit)

        self.pb_add.clicked.connect(self.addQuery)
        self.pb_remove.clicked.connect(self.removeQuery)

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.getFields()

   

    def getFields(self): # 0  EN COURS DE DEV ------------------------------------------------

# POUR RÉCUPÉRER LES CHAMP DE LA VUE : 
            self.lw_fields.clear()
            self.dico.clear()
            self.dico_fields_name_type.clear()
    
            
            db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            db.setHostName(self.host)
            db.setPort(self.port)
            db.setDatabaseName(self.bdd)
            db.setUserName(self.username)
            db.setPassword(self.psw)

            if (not db.open()):
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            else:

                wsql = "SELECT * FROM "+self.schema+"."+self.vue+"" 

                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                print(wsql)
                if not wquery.exec_() :
                    QMessageBox.critical(self, u"Impossible de récupérer les champs.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    field_names = []
                    for i in range(wquery.record().count()):
                        field_names.append(wquery.record().fieldName(i))
                        field_type = ""
                        # 2 = Integer // 6 = Real // 10 = Text // 14 = Date // 15 = Time
                        if wquery.record().field(i).type() == 2:
                            field_type = "Integer"
                        elif wquery.record().field(i).type() == 6:
                            field_type = "Real"
                        elif wquery.record().field(i).type() == 10:
                            field_type = "Text"
                        elif wquery.record().field(i).type() == 14:
                            field_type = "Date"
                        elif wquery.record().field(i).type() == 15:
                            field_type = "Time"
                        else:
                            field_type = "Unknown"
                        self.dico_fields_name_type[wquery.record().fieldName(i)] = field_type
                    print("Column Names:", field_names)

                    while wquery.next():

                        for i in range(wquery.record().count()):
                            value = wquery.value(i)
                            if field_names[i] not in self.dico:
                                self.dico[field_names[i]] = []
                            self.dico[field_names[i]].append(value)

                    if len(self.dico) > 0:
                        for field_names in self.dico.keys():  
                            self.lw_fields.addItem(str(field_names))
                    
                    else:
                        QMessageBox.information(self, "Information", "Pas de données additionnelles trouvées ", QMessageBox.Ok)
                  
                db.close()
                self.lw_fields.sortItems(Qt.AscendingOrder)

    def getValues(self):
        self.lw_values.clear() 

        selected_field = self.lw_fields.selectedItems()[0].text()
        print(selected_field)

        # print(selected_field[0].text())
        if selected_field in self.dico:
            distinct_values = set(self.dico[selected_field])
            for value in distinct_values : 
                # Détection du type de données
                if isinstance(value, int):
                    value = str(value)
                    if '.' in value:
                        value = value.split('.')[0]
                    self.lw_values.addItem(str(value))
                elif isinstance(value, str):
                    self.lw_values.addItem(str(value))
                elif isinstance(value, bool):
                    self.lw_values.addItem(str(value))
                elif isinstance(value, QDate):
                    # Vérification si la valeur est une date
                    value = value.toString('yyyy-MM-dd')
                    self.lw_values.addItem(str(value))
                else:
                    self.lw_values.addItem(str(value))  # Si le type n'est pas reconnu, le traiter comme un texte

        else:
            QMessageBox.information(self, "Information", f"Pas de valeurs trouvées", QMessageBox.Ok)

        self.lw_values.sortItems(Qt.AscendingOrder)
        self.le_selectfield.setText(selected_field)
        self.le_selectfieldType = ""
    
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
            logical = " "

        else:
            logical = self.cb_logical.currentText()
            if self.cb_logical.currentText() == "ET":
                logical =" AND "
            elif self.cb_logical.currentText() == "OU":
                logical =" OR "

            # print(self.cb_logical.currentText())
            # print(logical)
            
        field = self.le_selectfield.text()
         # if self.cb_operator.currentText() 
        value = self.le_selectvalue.text()

        # Traduction des types
        field_type = self.dico_fields_name_type[field]
        if field_type == "Integer":
            field_type = "::int"
        elif field_type == "Real":
            field_type = "::float"
        elif field_type == "Text":
            field_type = "::text"
        elif field_type == "Date":
            field_type = "::date"
        elif field_type == "Time":
            field_type = "::time"
        elif field_type == "Boolean":
            field_type = "::boolean"
        elif field_type == "Unknown":
            field_type = ""

        # Traduction des Opérateurs 
        operator_value = ""

        if field_type in ["::int", "::float", "::boolean"]:
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
        else:
            if self.cb_operator.currentText() == "COMMENCE PAR":
                operator_value =f" ILIKE '{value}%' "
            elif self.cb_operator.currentText() == "CONTIENT":
                operator_value = f" ILIKE '%{value}%' "
            elif self.cb_operator.currentText() == "FINI PAR":
                operator_value = f" ILIKE '%{value}' "
            elif self.cb_operator.currentText() == "PAS EGAL":
                operator_value = f" != '{value}' "
            elif self.cb_operator.currentText() == "EGAL":
                operator_value = f" = '{value}' "
            elif self.cb_operator.currentText() == ">":
                operator_value = f" > '{value}' "
            elif self.cb_operator.currentText() == "<":
                operator_value = f" < '{value}' "
            elif self.cb_operator.currentText() == ">=":
                operator_value = f" >= '{value}' "
            elif self.cb_operator.currentText() == "<=":
                operator_value = f" <= '{value}' "


        # print(self.cb_operator.currentText())
        # print(operator_value)
        query = ""
        if self.le_selectvalue.text() != "" and self.le_selectfield.text() != "":
            if "ILIKE" in operator_value and field_type in ["::int", "::float", "::boolean"]:
                query = f"{logical} \"{field}\"::text {operator_value}"
            else:
                query = f"{logical} \"{field}\"{field_type} {operator_value}"  
        else:
            QMessageBox.information(self, "Information", "veuillez sélectionner une valeur", QMessageBox.Ok)

        if query != "":
            item = QListWidgetItem(query)
            self.lw_queryresult.addItem(item)
         

    def removeQuery(self):
        selected_items = self.lw_queryresult.selectedItems()
        if selected_items:
            for item in selected_items:
                self.lw_queryresult.takeItem(self.lw_queryresult.row(item))

    def reject(self):
        self.lw_fields.clear()
        self.lw_values.clear() 
        self.dico = {}
        self.lw_queryresult.clear()
        self.filter_result.clear()
        QDialog.reject(self)

    def accept(self):
        for i in range(self.lw_queryresult.count()):
            self.filter_result.append(self.lw_queryresult.item(i).text())
        print(self.filter_result)
        QDialog.accept(self)



