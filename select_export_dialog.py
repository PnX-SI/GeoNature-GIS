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
form_select_export, _ = uic.loadUiType(os.path.join(ui_path, "select_export.ui"))




class SelectExportWidget(QDialog, form_select_export):
    def eventFilter(self, obj, event): # Fonction pour emêcher le bouton Ok de prendre le focus sur la touche Entrée
        if obj == self.le_select and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.filtreRechercher()
                return True
        return super().eventFilter(obj, event)


    def __init__(self, interfaceFenetres, whost, wport, wbdd, wusername, wpsw, parent=None):
        self.interfaceFenetres = interfaceFenetres

        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        self.selected_export_name = []  
        self.selected_view_schema = []
        self.selected_view_name = []
        self.geom_field = []
        self.srid = []
        self.description = []
        self.pk_column =[]

        self.filterText = ""
        self.pb_rechercher.clicked.connect(self.filtreRechercher)
        # Permet d'executer la fonction filtreRechercher() lors de l'appui sur la touche Entrée sur le lineEdit
        self.le_select.installEventFilter(self)
        self.le_select.returnPressed.connect(self.filtreRechercher)

        self.lw_list_view.itemSelectionChanged.connect(self.maj_lbl_descript_detail)  # Ajout du signal
        
        self.getExports(self.filterText)


    def getExports(self, filterText):

        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.host)
        db.setPort(self.port)
        db.setDatabaseName(self.bdd)
        db.setUserName(self.username)
        db.setPassword(self.psw)
        

        
        if (not db.open()):
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
        else:
                wsql =  "SELECT CONCAT(t_exports.id, ' - ', t_exports.label) as id_label, t_exports.desc , t_exports.schema_name, t_exports.view_name, geometry_field , geometry_srid, view_pk_column "
                wsql += "FROM gn_exports.t_exports "
                wsql += "WHERE CONCAT(t_exports.id, ' - ', t_exports.label) ILIKE '%" + filterText + "%' "
                wsql += "ORDER BY t_exports.id;"

                # print(wsql)
                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    QMessageBox.critical(self, u"Impossible de récupérer les Exports.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    self.lw_list_view.clear()
                    while wquery.next():
                        # on crée un item qui contient à la fois le texte présenté à l'utilisateur
                        item = QListWidgetItem(f"{wquery.value(0)}")
                        # et les données associées
                        data = (wquery.value(0), wquery.value(1), wquery.value(2), wquery.value(3), wquery.value(4), wquery.value(5), wquery.value(6))
                        item.setData(Qt.UserRole, data) #256 = constante renvoyée par Qt.UserRole (bug avec Qt.UserRole sur certains pc)
                        self.lw_list_view.addItem(item)
                
                db.close()

                # self.lw_list_view.sortItems(Qt.AscendingOrder)

    def filtreRechercher(self):
        self.filterText = self.le_select.text()
        print(self.filterText)
        self.getExports(self.filterText)

    def maj_lbl_descript_detail(self):
        # Mettre à jour le texte du label avec la description de l'export sélectionné
            self.description = []
            for selection in self.lw_list_view.selectedItems():
                data = selection.data(Qt.UserRole)
                self.description.append(data[1])
            self.lbl_descript_detail.setText(f"{self.description}")


    def reject(self):
        self.filterText = []
        self.le_select.clear() 
        self.lw_list_view.clear()
        self.selected_view_path = ""
        
        self.selected_export_name = []  
        self.selected_view_schema = []
        self.selected_view_name = []
        self.geom_field = []
        self.srid = []
        self.description = []
        self.pk_column =[]
        QDialog.reject(self)



    def accept(self):
        # récupération des valeurs de champs associés à la vue sélectionnée

        if len(self.lw_list_view.selectedItems()) > 0:

            # selection = self.lw_list_view.selectedItems()[0].text()
            for selection in self.lw_list_view.selectedItems():
                # print(selection)
                data = selection.data(Qt.UserRole)
                # print(data)
                # print(selection.data(256))

                self.selected_export_name.append(data[0])
                self.description.append(data[1])
                self.selected_view_schema.append(data[2])
                self.selected_view_name.append(data[3])
                self.geom_field.append(data[4])
                self.srid.append(data[5])
                self.pk_column.append(data[6])

            QDialog.accept(self)

        else: 
            QMessageBox.warning(self, u"Aucun Export sélectionné.", u"Veuillez sélectionner un export.", QMessageBox.Ok)




