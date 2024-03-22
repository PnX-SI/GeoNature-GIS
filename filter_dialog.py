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

    def __init__(self, interfaceFenetres, whost, wport, wbdd, wusername, wpsw, parent=None):
        self.interfaceFenetres = interfaceFenetres

        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        

        # self.filterText = ""
        # self.pb_rechercher.clicked.connect(self.filtreRechercher)


        # self.resultView = []

        
        
        # self.getViews(self.filterText)
   

   


    def filtreRechercher(self):
        filterText = self.le_select.text()
        print(self.typeZone)
        print(filterText)
        self.getZone(self.typeZone, filterText)

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
            
        field = self.le_select_field.text()
         # if self.cb_operator.currentText() 
        value = self.le_select_value.text()

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
    
        query = f"{logical} {field} {operator_value}"
        item = QListWidgetItem(query)
        self.lw_queryresult.addItem(item)
         



    def reject(self):
        QDialog.reject(self)



    def accept(self):
        self.getResultZone()
        QDialog.accept(self)



