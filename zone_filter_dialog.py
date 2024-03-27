# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.uic import *
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *
import sys, os

import os


ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_filter_zonage, _ = uic.loadUiType(os.path.join(ui_path, "filter_zonage.ui"))




class ZoneFilterWidget(QDialog, form_filter_zonage):

    def __init__(self, interfaceFenetres, whost, wport, wbdd, wusername, wpsw, typeZone, parent=None):
        self.interfaceZoneFilter = interfaceFenetres

        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        self.typeZone = "".join(typeZone)


        self.filterText = ""
        self.pb_rechercher.clicked.connect(self.filtreRechercher)


        self.resultZone = []

        
        
        self.getZone(self.typeZone, self.filterText)
   


    def getZone(self, typeZone, filterText):
        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.host)
        db.setPort(self.port)
        db.setDatabaseName(self.bdd)
        db.setUserName(self.username)
        db.setPassword(self.psw)

        
        if (not db.open()):
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
        else:
            if filterText != "":
                print("FILTRE")
                wsql = "SELECT DISTINCT nom FROM "
                wsql += "(SELECT DISTINCT id_type, area_name as nom FROM ref_geo.l_areas "
                wsql += "UNION SELECT DISTINCT id_type, linear_name as nom FROM ref_geo.l_linears "
                wsql += "UNION SELECT DISTINCT id_type, point_name as nom FROM ref_geo.l_points) as rq0 "
                wsql += "WHERE (id_type = " + typeZone + ") AND (nom ILIKE '"+ filterText + "%') "
                wsql += "ORDER BY nom;"
                print(wsql)
                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    QMessageBox.critical(self, u"Impossible de récupérer les nom des zonages.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    self.lw_list_zone.clear()
                    while wquery.next():
                        # on crée un item qui contient à la fois le texte présenté à l'utilisateur
                        item = QListWidgetItem(f"{wquery.value(0)}")
                        # et les données associées
                        data = (wquery.value(0))
                        item.setData(256, data)
                        self.lw_list_zone.addItem(item)

                db.close()

            else:
                print ("PAS FILTRE")
                wsql = "SELECT DISTINCT nom FROM "
                wsql += "(SELECT DISTINCT id_type, area_name as nom FROM ref_geo.l_areas "
                wsql += "UNION SELECT DISTINCT id_type, linear_name as nom FROM ref_geo.l_linears "
                wsql += "UNION SELECT DISTINCT id_type, point_name as nom FROM ref_geo.l_points) as rq0 "
                wsql += "WHERE (id_type = " + typeZone + ") "
                wsql += "ORDER BY nom;"
                wquery = QSqlQuery(db)
                print(wsql)
                # print(typeZone)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    QMessageBox.critical(self, u"Impossible de récupérer les nom des zonages.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    self.lw_list_zone.clear()
                    while wquery.next():
                        # on crée un item qui contient à la fois le texte présenté à l'utilisateur
                        item = QListWidgetItem(f"{wquery.value(0)}")
                        # et les données associées
                        data = (wquery.value(0))
                        item.setData(256, data)
                        self.lw_list_zone.addItem(item)


                db.close()


    


    def filtreRechercher(self):
        filterText = self.le_select.text()
        print(self.typeZone)
        print(filterText)
        self.getZone(self.typeZone, filterText)



    def reject(self):
        QDialog.reject(self)



    def accept(self):
       
        for uneSelection in self.lw_list_zone.selectedItems():
            data = uneSelection.data(256)
            result = data
            result = result.replace("'","''")
            self.resultZone.append(str(result))
        print(self.resultZone)
        
        QDialog.accept(self)