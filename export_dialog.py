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
        self.interfaceFenetres = interface
        QDockWidget.__init__(self)
        self.setupUi(self)

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw

        # Fonction réinitialisation des paramètres des filtes 
        self.pb_reset.clicked.connect(self.reinitialisation)

        # Fonction pour ouvrir l'aide
        self.pb_help.clicked.connect(util_dialog.openHelp)

        self.pb_selectview.clicked.connect(self.openSelectExport)

        self.pb_addfilter.clicked.connect(self.openFilter)

        self.pb_runquery.clicked.connect(self.executer)

        self.pb_loadlayer.clicked.connect(self.loadInQGIS)

        self.pb_quit.clicked.connect(self.quitter)




    def openSelectExport(self):
        self.connexion = SelectExportWidget(self.interfaceFenetres, self.host, self.port, self.bdd, self.username, self.psw)
        # connexion.show()
        result = self.connexion.exec_()
        if result:
            return self.connexion.selected_view_name , self.connexion.description , self.connexion.selected_view_path, self.connexion.geom_field, self.connexion.srid, self.maj_lbl_nom_export(), self.maj_lbl_description()


    
    def openFilter(self):
        self.connexion = FilterWidget(self.interfaceFenetres, self.host, self.port, self.bdd, self.username, self.psw)
        # connexion.show()
        result = self.connexion.exec_()
        if result:
            pass


    def maj_lbl_nom_export(self):
        # Mettre à jour le texte du label avec la description de l'export sélectionné
            nom_export = self.connexion.selected_view_name[0]
            self.lbl_viewname.setText(nom_export)


    def maj_lbl_description(self):
        # Mettre à jour le texte du label avec la description de l'export sélectionné
            description = self.connexion.description[0]
            self.lbl_viewdescription.setText(description)




    def executer(self):

        nom_export = self.connexion.selected_view_name[0]
        view_path = self.connexion.selected_view_path[0]
        srid = self.connexion.srid[0]
        filter = ""

        wuri = QgsDataSourceUri()

        # set host name, port, database name, username and password
        wuri.setConnection("162.19.89.37", "5432", "geonature2db", "lupsig2024", "fdmMP8rYr!ebCQLy") # FOR TESTING ONLY - TO BE DELETED
        # wuri.setConnection("localhost", "5432", "postgres" , "postgres", "123465")------- FONCTIONNE BDD LOCALE --------
        # wuri.setDataSource("eval", "zh", "geom") ------- FONCTIONNE BDD LOCALE --------
        
        if self.connexion.selected_view_name != [] :

                # set database schema, table name, geometry column and optionally
                # subset (WHERE clause)
            sql = "(SELECT * FROM " + view_path + " WHERE " + filter + ")"
            # uri.setDataSource("", sql, "geom", "", "id_areas")

            wuri.setDataSource("lposep", "v_occtax", "geom_4326")


           # ------------------ FONCTIONNE --------------------------------
            #wuri.setDataSource("eval", "zh", "geom")

            vlayer = QgsVectorLayer(wuri.uri(), f"{nom_export}_{srid}", "postgres")
            if vlayer.isValid():
                print("vlayer valide")
                QgsProject.instance().addMapLayer(vlayer, False)
            else:
                print("vlayer non valid")
                
    def loadInQGIS(self):
         
         QgsProject.instance().addMapLayer(vlayer, True)

    def reinitialisation(self):

        print('Réinitialisé !')

        #Export
        self.connexion.selected_view_name = [] 
        self.connexion.description = []
        self.connexion.selected_view_path = []
        self.connexion.geom_field = []
        self.connexion.srid = []

        #Filtre 
        


    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["export"])
        event.accept()

    def quitter(self):
        self.close()