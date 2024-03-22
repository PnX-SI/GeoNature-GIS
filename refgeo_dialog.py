# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt5 import *
from PyQt5 import uic
from PyQt5.uic import *
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import sys, os

from .geonaturegisPlugin import * 
from .additional_data_filter_dialog import *
import util_dialog
from .zone_filter_dialog import *
# import zone_filter_dialog

# important pour PyQt5 et gestion du fichier resources.qrc
sys.path.append(os.path.dirname(__file__))
from .resources_rc import *
# compilation de la façon suivante :
# - ouverture osgeo4w shell
# - déplacement dans le répertoire : cd C:\Users\a.layec\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\Geonature-GIS-main
# - compilation : pyrcc5 resources.qrc -o resources_rc.py

ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_refgeo, _ = uic.loadUiType(os.path.join(ui_path, "referentiel_geographique_dock.ui"))

class RefGeoWidget(QDockWidget, form_refgeo):
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


        self.filtre_additionnel = ""
# ----------------------------- ------------------ CONNEXION DES WIDGET --------------------------------------------------------

        # Fonction réinitialisation des paramètres des filtes 
        self.pb_reset.clicked.connect(self.reinitialisation)

        # Fonction pour ouvrir l'aide
        self.pb_help.clicked.connect(util_dialog.openHelp)


        # Fonctions pour tout cocher ou tout décocher dans la CheckableComboBox contenant les sources (ccb_source)
        self.pb_check.clicked.connect(self.check_all)
        self.pb_uncheck.clicked.connect(self.uncheck_all)


        # Vérouille ou dévérouille le bouton "Filtrer le zonage" en fonction du nombre de sélection du type de zonage
        self.lw_zonage.itemSelectionChanged.connect(self.lockZoneFilter)

        # Connexion à la fenêtre "Sélection du zonage"
        self.pb_filterzonage.clicked.connect(self.openZoneFilter)

        # Initialisation du nombre de sources sélectionnées
        # self.maj_lbl_sourceselectcount()
        # Fonction pour mettre à jour le nombre de sources sélectionnées quand une case est cocher ou décocher dans ccb_source
        self.ccb_source.checkedItemsChanged.connect(self.maj_lbl_sourceselectcount) # Ajout du signal

        # Fonction pour mettre à jour le nombre de sources sélectionnées quand une case est cocher ou décocher dans ccb_source
        self.lw_zonage.itemSelectionChanged.connect(self.maj_lbl_zonageparam)  # Ajout du signal

        # pour test sélection AOT
        self.pb_test_selection.clicked.connect(self.test_selection)
    

        # Fonction de connexion à la fenêtre additional_data_filter_dialog
        self.pb_additionalFilter.clicked.connect(self.openAddDataFilter)
        self.lw_zonage.itemSelectionChanged.connect(self.lockAddDataFilter)

        #  Pour Instancier les valeurs de la QcheckableComboBox (ccb_source) concernant les sources en fonction des valeurs via dans lw_source
        self.lw_zonage.itemSelectionChanged.connect(self.selection_typeZonage)

        self.rdb_no.toggled.connect(self.enableStatut)
        self.rdb_yes.toggled.connect(self.enableStatut)
        self.rdb_na.toggled.connect(self.enableStatut)


        # Fonction d'execution des filtre
        self.pb_runquery.clicked.connect(self.filterExecuter)


        # Fermer la fenêtre
        self.pb_quit.clicked.connect(self.quitter)


# ------------------------------------------------ VARIABLES DE CLASSE --------------------------------------------
#  Pour Instancier la liste qui vient alimenter le QlistWidget (lw_zonage) concernant le type de zonage 
        self.typeZone = []
        self.table = []
        self.source = []
        self.connexionZonage = []
        self.connexionAddFilter = []
        self.enable = ""
        self.getTypeZonage()


# ------------------------------------------------ PARAMETRES AVANCES ----------------------------------------------------------------
# 0 - EN COURS - Ajout des valeurs de la sélection de l'état du champ "enable" (géométrie active dans géonature)
#  pour filtrer sur le champ "enable" (Géométrie active dans Géonature) avec les radio boutons  
    def enableStatut(self):

        if self.rdb_no.isChecked() == True:
            self.enable = "enable IS NOT true"
           
        elif self.rdb_yes.isChecked() == True : 
            self.enable = "enable IS true"

        elif self.rdb_na.isChecked() == True :
            self.enable = ""


# ----------------------------- ------------------ DEFINITION DES METHODES --------------------------------------------------------
   

    def selection_typeZonage(self):  # Filtrer les sources en fonction du/des types de zonages sélectionnés 
        # typeZone = []
        
        if len(self.lw_zonage.selectedItems()) >=1 :
            self.typeZone.clear()
            self.table.clear()
        # récupération des types de zonages sélectionnés de la QListWidget "lw_zonage"
            for uneSelection in self.lw_zonage.selectedItems():
                #print(uneSelection.data(256))
                data = uneSelection.data(256) #256 = constante renvoyée par Qt.UserRole (bug avec Qt.UserRole sur certains pc)
                nomtable = data[2]
                id_type = data[3]

                self.typeZone.append(str(id_type))  
                self.table.append(str(nomtable))    

            self.getSource(self.typeZone)
            self.selection_table()
            return self.typeZone, self.table
    
         #  - ----------------------------------------------------------------        
        
    def selection_table(self):  # Filtrer les sources en fonction du/des types de zonages sélectionnés 

        self.tableAreas = ""
        self.tableLinears = ""
        self.tablePoints = ""      
        
        for i in self.table:
            
            self.unique = i
            print(self.unique)
            

            if self.unique == "l_areas" :
                self.tableAreas = self.unique
            elif self.unique == "l_linears":
                self.tableLinears = self.unique
            elif self.unique == "l_points":
                self.tablePoints = self.unique
     
        # print(self.table)
        return self.tableAreas, self.tableLinears, self.tablePoints
             
    #  - ----------------------------------------------------------------
        


    def selection_source(self):  # Pour récupérer la/les sources sélectionnée

        self.source = str(self.ccb_source.checkedItems())
       
        return self.source
             
    # 0 - ----------------------------------------------------------------

    def test_selection(self):
        # typeZone = []
        # # récupération des zonages sélectionnés de la QListWidget "lw_zonage"
        # for uneSelection in self.lw_zonage.selectedItems():
        #     # print(uneSelection.text() + " AND")
        #     print(uneSelection.data(256))
        #     data = uneSelection.data(256)
        #     id_type = data[3]
        #     typeZone.append(str(id_type))
        #     return id_type
        # self.getSource(typeZone)
        # print(f"typeZone : {id_type}")

        # récupération des sources cochées de la QgsCheckableComboBox "ccb_source"
        selectedsource = []
        item = self.ccb_source.checkedItems()
        selectedsource.append(item)

        # selected_items = []
        # for item in self.ccb_source.checkedItems():
        #     selected_items.append(item.text())

        # Access the list of checked items
        # print(selected_items)
        # for i in self.ccb_source.checkedItems():
        #     selectedsource.append(self.ccb_source.itemText(i))
        #     # print(uneSelection + " AND")
        print(selectedsource)
        # listSelection = []

        # for uneSelection in self.ccb_source.checkedItems():
        #     uneSelection = uneSelection.text()
        #     listSelection.append(uneSelection)
        # print(listSelection)
        # récupération de toutes les sources de "ccb_source" si aucune n'est cochée
        if len(self.ccb_source.checkedItems()) == 0:
            lst_element = []
            for i in range(self.ccb_source.count()):
                lst_element.append(self.ccb_source.itemText(i))
            print("lst_element : ", lst_element)


    
    # Ajout des valeurs de la sélection du type de zonage
    def getTypeZonage(self):
        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.host)
        db.setPort(self.port)
        db.setDatabaseName(self.bdd)
        db.setUserName(self.username)
        db.setPassword(self.psw)

        if (not db.open()):
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
        else:
            wsql = "SELECT DISTINCT type_name, type_obj, nom_table, id_type FROM  "
            wsql += "(SELECT DISTINCT type_name, 'surface' as type_obj, 'l_areas' as nom_table, id_type FROM ref_geo.bib_areas_types UNION "
            wsql +="SELECT DISTINCT type_name, 'ligne' as type_obj, 'l_linears' as nom_table, id_type FROM ref_geo.bib_linears_types UNION "
            wsql +="SELECT DISTINCT type_name, 'point' as type_obj, 'l_points' as nom_table, id_type FROM ref_geo.bib_points_types) as rq0 " 
            wsql += "WHERE type_name IS NOT NULL "
            wsql += "ORDER BY type_name, type_obj;"
            wquery = QSqlQuery(db)
            wquery.prepare(wsql)
            if not wquery.exec_():
                QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wquery.lastError().text(), QMessageBox.Ok)
            else:
                # pour chaque ligne
                while wquery.next():
                    # on crée un item qui contient à la fois le texte présenté à l'utilisateur
                    item = QListWidgetItem(f"{wquery.value(0)} - {wquery.value(1)}")
                    # et les données associées
                    data = (wquery.value(0), wquery.value(1), wquery.value(2), wquery.value(3))
                    # item.setData(256, data)
                    item.setData(256, data) #256 = constante renvoyée par Qt.UserRole (bug avec Qt.UserRole sur certains pc)
                    self.lw_zonage.addItem(item)

            db.close()

                                                   


# 0 - EN COURS DE DEV --------------------------------------------------------------------------------

# Ajout des valeurs de la sélection des sources
    def getSource(self, typeZone):
        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.host)
        db.setPort(self.port)
        db.setDatabaseName(self.bdd)
        db.setUserName(self.username)
        db.setPassword(self.psw)

        if len(typeZone) == 0:
            self.ccb_source.clear()
            self.maj_lbl_sourceselectcount()
        else:
            if (not db.open()):
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            else:
                wsql = "SELECT DISTINCT source FROM "
                wsql += "(SELECT DISTINCT id_type, source FROM ref_geo.l_linears "
                wsql += "UNION SELECT DISTINCT id_type, source FROM ref_geo.l_points "
                wsql += "UNION SELECT DISTINCT id_type, source FROM ref_geo.l_areas ) as rq0 "
                wsql += "WHERE id_type IN (" + ", ".join(typeZone)  + ") "
                wsql += "ORDER BY source;"
                wquery = QSqlQuery(db)
                wquery.prepare(wsql)
                if not wquery.exec_():
                    # QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wquery.lastError().text(), QMessageBox.Ok)
                    QMessageBox.critical(self, u"Impossible de récupérer les sources.", wquery.lastError().text(), QMessageBox.Ok)
                else:
                    self.ccb_source.clear()
                    while wquery.next():
                        # print("wquery.value(0) : ", wquery.value(0))
                        if str(wquery.value(0)) == 'NULL' :
                            self.ccb_source.addItemWithCheckState("Non-renseigné", False, None)
                        else:
                            self.ccb_source.addItemWithCheckState(str(wquery.value(0)), False, None)

                db.close()
# 0---------------------------------------------------------------------------------



    def check_all(self):
            # Cocher toutes les cases de la QComboBox
            self.ccb_source.selectAllOptions()


    def uncheck_all(self):
            # Déocher toutes les cases de la QComboBox
            self.ccb_source.deselectAllOptions()

    def maj_lbl_sourceselectcount(self):
            # Mettre à jour le texte du label
                
            self.lbl_sourceselectcount.setText(f"{len(self.ccb_source.checkedItems())} source(s) sélectionnée(s)")

#  Afficher la sélection du / des type(s) de zonage(s) dans le label lbl_zonageparam
    def maj_lbl_zonageparam(self):
                # Mettre à jour le texte du label
            listSelection = []
            for uneSelection in self.lw_zonage.selectedItems():
                uneSelection = uneSelection.text()
                listSelection.append(uneSelection)
            self.lbl_zonageparam.setText(f"Type(s) de zonage(s) sélectionné(s) : {listSelection}")


    def reinitialisation(self):
        print('Réinitialisé !')

        #Zonage
        self.lw_zonage.clearSelection()
        self.typeZone = []
        self.connexionZonage = []

        #Source
        self.ccb_source.deselectAllOptions()

        #Enable
        self.rdb_na.setChecked(True)

        #Filtre additionel
        self.connexionAddFilter = []


    def lockZoneFilter(self):
        if len(self.lw_zonage.selectedItems()) == 1:
            self.pb_filterzonage.setEnabled(True)
            self.pb_filterzonage.setStyleSheet("QPushButton:enabled { color: rgb(5, 144, 110) }")
        else:
            self.pb_filterzonage.setEnabled(False)
            self.pb_filterzonage.setStyleSheet("QPushButton:disabled { color: gray }")

    def openZoneFilter(self):
        typeZonage = self.typeZone
        self.connexionZonage = ZoneFilterWidget(self.interfaceFenetres, self.host, self.port, self.bdd, self.username, self.psw, typeZonage)
        result = self.connexionZonage.exec_()
        if result:
            return self.connexionZonage.resultZone



    def lockAddDataFilter(self):
        if len(self.lw_zonage.selectedItems()) > 0:
            self.pb_additionalFilter.setEnabled(True)
            self.pb_additionalFilter.setStyleSheet("QPushButton:enabled { color: rgb(5, 144, 110) }")
        else:
            self.pb_additionalFilter.setEnabled(False)
            self.pb_additionalFilter.setStyleSheet("QPushButton:disabled { color: gray }")



    def openAddDataFilter(self):
        typeZone = self.typeZone
        self.connexionAddFilter = AddDataFilterWidget(self.interfaceFenetres, self.host, self.port, self.bdd, self.username, self.psw, typeZone )
        result = self.connexionAddFilter.exec_()
        if result:
            print(self.connexionAddFilter.adf_resultat)

    def filterExecuter(self):
        # db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        # db.setHostName(self.host)
        # db.setPort(self.port)
        # db.setDatabaseName(self.bdd)
        # db.setUserName(self.username)
        # db.setPassword(self.psw)


        wuri = QgsDataSourceUri()

        # set host name, port, database name, username and password
        # wuri.setConnection("162.19.89.37", "5432", "geonature2db", "lupsig2024", "fdmMP8rYr!ebCQLy")D# FOR TESTING ONLY - TO BE DELETE
        wuri.setConnection("localhost", "5432", "postgres" , "postgres", "123456")# FOR TESTING ONLY - TO BE DELETE -- FONCTIONNE
        # wuri.setDataSource("eval", "zh", "geom") ------- FONCTIONNE BDD LOCALE --------
        
        if self.tableAreas != "" :

              # ------------------ FONCTIONNE --------------------------------
            wuri.setDataSource("eval", "zh", "geom")

            vlayer = QgsVectorLayer(wuri.uri(), "layer name you like", "postgres")
            if vlayer.isValid():
                print("vlayer valide")
                QgsProject.instance().addMapLayer(vlayer)
            else:
                print("vlayer non valid")

            # if self.connexionZonage != []:
            # print("TEST -------------------------------------------")
            # print("passe par " + self.tableAreas)
            # print(self.typeZone)
            # print(self.connexionZonage.resultZone)
            # print(self.source)
            # print(self.enable)
            # print(self.connexionAddFilter.adf_resultat)

                # set database schema, table name, geometry column and optionally
                # subset (WHERE clause)
            # sql = "(SELECT * FROM ref_geo.l_areas WHERE id_type=26 AND geom IS NOT NULL)"
            # uri.setDataSource("", sql, "geom", "", "id_areas")

            # wuri.setDataSource("ref_geo", "sql", "geom", "id_type = " + ", ".join(self.typeZone))
            # wuri.setDataSource("ref_geo", "l_areas", "geom", "geom IS NOT NULL AND l_areas.id_type = 26")      
                
                # une_couche_vectorielle = QgsVectorLayer(uri.uri(), "comtest", "postgres")
            # if self.connexionAddFilter!= []:

                # print(uri.setDataSource)


        if self.tableLinears != "" :
            print("TEST -------------------------------------------")
            print("passe par " + self.tableLinears)
            print(self.typeZone)
            print(self.connexionZonage.resultZone)
            print(self.source)
            print(self.enable)
            print(self.connexionAddFilter.adf_resultat)



        if self.tablePoints != "" :
            print("TEST -------------------------------------------")
            print("passe par " + self.tablePoints)
            print(self.typeZone)
            print(self.connexionZonage.resultZone)
            print(self.source)
            print(self.enable)
            print(self.connexionAddFilter.adf_resultat)
        

        # print(self.connexionAddFilter.adf_resultat)


        # if (not db.open()):
        #     QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
        # else:
        #     wsql = "SELECT * FROM  "

        #     wsql += "(SELECT DISTINCT type_name, 'surface' as type_obj, 'ref_geo.bib_areas_types' as nom_table, id_type FROM ref_geo.bib_areas_types UNION "
        #     wsql +="SELECT DISTINCT type_name, 'ligne' as type_obj, 'ref_geo.bib_linears_types' as nom_table, id_type FROM ref_geo.bib_linears_types UNION "
        #     wsql +="SELECT DISTINCT type_name, 'point' as type_obj, 'ref_geo.bib_points_types' as nom_table, id_type FROM ref_geo.bib_points_types) as rq0 " 
        #     wsql += "WHERE (type_name IS NOT NULL) AND id_type = "
        #     wsql += "ORDER BY type_name, type_obj;"
        #     wquery = QSqlQuery(db)
        #     wquery.prepare(wsql)

    def loadInQGIS(self) :

        QgsProject.instance().addMapLayer(vlayer, True)
        # vlayer = iface.addVectorLayer(path_to_airports_layer, "Airports layer", "ogr")
        # if not vlayer:
        #     print("Layer failed to load!")

        # # The format is:
        # # vlayer = QgsVectorLayer(data_source, layer_name, provider_name)

        # vlayer = QgsVectorLayer(path_to_airports_layer, "Airports layer", "ogr")
        # if not vlayer.isValid():
        #     print("Layer failed to load!")
        # else:
        #     QgsProject.instance().addMapLayer(vlayer)


        # uri = QgsDataSourceUri()
        # # set host name, port, database name, username and password
        # uri.setConnection("localhost", "5432", "dbname", "johny", "xxx")
        # # set database schema, table name, geometry column and optionally
        # # subset (WHERE clause)
        # uri.setDataSource("public", "roads", "the_geom", "cityid = 2643", "primary_key_field")

        # vlayer = QgsVectorLayer(uri.uri(), "layer name you like", "postgres")


    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["refgeo"])
        event.accept()


    def quitter(self):
        self.close()
