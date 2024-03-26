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

        # Fonction pour mettre à jour le nombre de sources sélectionnées quand une case est cocher ou décocher dans ccb_source
        self.ccb_source.checkedItemsChanged.connect(self.maj_lbl_sourceselectcount) # Ajout du signal
        self.ccb_source.checkedItemsChanged.connect(self.selection_source) # Ajout du signal

        # Fonction pour mettre à jour le nombre de sources sélectionnées quand une case est cocher ou décocher dans ccb_source
        self.lw_zonage.itemSelectionChanged.connect(self.maj_lbl_zonageparam)  # Ajout du signal
    

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
            self.enable = "AND enable IS NOT true"
           
        elif self.rdb_yes.isChecked() == True : 
            self.enable = "AND enable IS true"

        elif self.rdb_na.isChecked() == True :
            self.enable = ""


# ----------------------------- ------------------ DEFINITION DES METHODES --------------------------------------------------------
   

    def selection_typeZonage(self):  # Filtrer les sources en fonction du/des types de zonages sélectionnés 
        # typeZone = []

        
        self.tableAreas = ""
        self.tableLinears = ""
        self.tablePoints = ""      
        
        
        if len(self.lw_zonage.selectedItems()) >=1 :
            self.typeZone.clear()
            self.table.clear()
        # récupération des types de zonages sélectionnés de la QListWidget "lw_zonage"
            for uneSelection in self.lw_zonage.selectedItems():
                #print(uneSelection.data(256))
                data = uneSelection.data(256) #256 = constante renvoyée par Qt.UserRole (bug avec Qt.UserRole sur certains pc)
                nomtable = data[2]
                id_type = data[3]
                if nomtable == "l_areas" :
                    self.tableAreas = "l_areas"
                elif nomtable == "l_linears" :
                    self.tableLinears = "l_linears"
                elif nomtable == "l_points" :
                    self.tablePoints = "l_points"  

                self.typeZone.append(str(id_type))  
                self.table.append(str(nomtable))    

            self.getSource(self.typeZone)
            # self.selection_table()
            return self.typeZone, self.table, self.tableAreas, self.tableLinears, self.tablePoints
    
    #  - ----------------------------------------------------------------        
        

    def selection_source(self):  # Pour récupérer la/les sources sélectionnée

        self.source = self.ccb_source.checkedItems()
       
        return self.source
             
    # 0 - ----------------------------------------------------------------
    
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
            wsql = "WITH ref_geo_types AS "
            wsql += "	(SELECT DISTINCT type_name, 'surface' as type_obj, 'l_areas' as nom_table, id_type FROM ref_geo.bib_areas_types UNION "
            wsql += " 	 SELECT DISTINCT type_name, 'ligne' as type_obj, 'l_linears' as nom_table, id_type FROM ref_geo.bib_linears_types UNION "
            wsql += " 	 SELECT DISTINCT type_name, 'point' as type_obj, 'l_points' as nom_table, id_type FROM ref_geo.bib_points_types), "
            wsql += "	count_ref_geo_types AS "
            wsql += "	(SELECT COUNT(id_area), 'surface' as type_obj, id_type FROM ref_geo.l_areas GROUP BY id_type HAVING COUNT(id_area) > 0 UNION "
            wsql += "	 SELECT COUNT(id_linear), 'ligne' as type_obj, id_type FROM ref_geo.l_linears GROUP BY id_type HAVING COUNT(id_linear) > 0 UNION "
            wsql += "	 SELECT COUNT(id_point), 'point' as type_obj, id_type FROM ref_geo.l_points GROUP BY id_type HAVING COUNT(id_point) > 0) "
            wsql += "SELECT DISTINCT rgt.type_name, rgt.type_obj, rgt.nom_table, rgt.id_type "
            wsql += "FROM ref_geo_types rgt "
            wsql += "JOIN count_ref_geo_types crgt ON crgt.id_type = rgt.id_type AND crgt.type_obj = rgt.type_obj "
            wsql += "WHERE rgt.type_name IS NOT NULL "
            wsql += "ORDER BY rgt.type_name, rgt.type_obj;"
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
        self.tableAreas = ""
        self.tableLinears = ""
        self.tablePoints = ""

        #Source
        self.source = ['']
        self.ccb_source.clear()
        self.ccb_source.deselectAllOptions()

        #Enable
        self.rdb_na.setChecked(True)

        #Filtre additionel
        self.connexionAddFilter = []

        #Type de géométrie trouvée
        self.lw_typegeomresult.clear()


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
        if len(self.lw_zonage.selectedItems()) == 1:
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
            return self.connexionAddFilter.adf_resultat, self.maj_lbl_filterparam()

    def maj_lbl_filterparam(self):   
        filtre = " ".join(self.connexionAddFilter.adf_resultat)
        self.lbl_filterparam.setText(f"WHERE {filtre}")




    def varWHERE(self):
        self.querywhere = ""
        if self.connexionZonage != []:
            self.querywhere += " AND area_name IN ('" + "', '".join(self.connexionZonage.resultZone) + "') "

        if self.connexionAddFilter != []:
            self.querywhere += "" + " ".join(self.connexionAddFilter.adf_resultat) + " "

        if self.source != []:
            if self.source == ['Non-renseigné'] :
                self.querywhere += " AND source IS NULL"

            elif (len(self.source) == 1) and (self.source != ['Non-renseigné']):
                self.querywhere += " AND source = '" + "', '".join(self.source) + "' "

            elif len(self.source) > 1:
                self.querywhere += " AND source IN ("

                for i in self.source:
                    if i != 'Non-renseigné':
                        self.querywhere += " '" + i + "', "
                        no_null = True

                    elif i == 'Non-renseigné':
                        self.querywhere = self.querywhere.rstrip(", ") + " ) AND IS NULL"
                        no_null = False

                if no_null == True:
                    self.querywhere = self.querywhere.rstrip(", ") + ") "
                

        print(self.querywhere)
        return self.querywhere

    def filterExecuter(self):
        self.lw_typegeomresult.clear()
        self.varWHERE()


        wuri = QgsDataSourceUri()

        # # set host name, port, database name, username and password
        wuri.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw)


        if self.tableAreas != "" :
            print("IT'S A POLYGON LAYER !")
            nbPolygonLayer = 0
            for i in(self.typeZone):
                # print(i)
                # print(self.source)
                wuri.setDataSource("ref_geo", "l_areas", "geom", "geom IS NOT NULL AND id_type = " + i + " " + self.enable + self.querywhere)
                # print("ref_geo", "l_areas", "geom", "geom IS NOT NULL AND id_type = " + i + " AND source = " + " OR ".join(self.source) + " " + self.enable)            

                vlayer = QgsVectorLayer(wuri.uri(), i, "postgres")
                if vlayer.isValid():
                    print("vlayer valide")
                    QgsProject.instance().addMapLayer(vlayer)
                    nbPolygonLayer += 1 
                else:
                    print("vlayer non valid")

            self.lw_typegeomresult.addItem("Polygone (" + str(nbPolygonLayer) + ")")


        if self.tableLinears != "" :
            print("IT'S A LINE LAYER !")
            nbLineLayer = 0
            for i in(self.typeZone):
                # vérifier que le type zone ne soit pas pris 2 fois ------------------- 
                # print(i)
                # print(self.source)
                wuri.setDataSource("ref_geo", "l_linears", "geom", "geom IS NOT NULL AND id_type = " + i + " " + self.enable + self.querywhere)
                # print("ref_geo", "l_areas", "geom", "geom IS NOT NULL AND id_type = " + i + " AND source = " + " OR ".join(self.source) + " " + self.enable)            

                vlayer = QgsVectorLayer(wuri.uri(), i, "postgres")
                if vlayer.isValid():
                    print("vlayer valide")
                    QgsProject.instance().addMapLayer(vlayer)
                    nbLineLayer += 1 
                else:
                    print("vlayer non valid")

            self.lw_typegeomresult.addItem("Line (" + str(nbLineLayer) + ")")


        if self.tablePoints != "" :
            print("IT'S A POINT LAYER !")
            nbPointLayer = 0
            for i in(self.typeZone):
                # print(i)
                # print(self.source)
                wuri.setDataSource("ref_geo", "l_points", "geom", "geom IS NOT NULL AND id_type = " + i + " " + self.enable + self.querywhere)
                # print("ref_geo", "l_areas", "geom", "geom IS NOT NULL AND id_type = " + i + " AND source = " + " OR ".join(self.source) + " " + self.enable)            

                vlayer = QgsVectorLayer(wuri.uri(), i, "postgres")
                if vlayer.isValid():
                    print("vlayer valide")
                    QgsProject.instance().addMapLayer(vlayer)
                    nbPointLayer += 1
                else:
                    print("vlayer non valid")
            
            self.lw_typegeomresult.addItem("Point (" + str(nbPointLayer) + ")")
        



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
