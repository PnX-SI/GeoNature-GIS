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


from .geonaturegisPlugin import * 
from .additional_data_filter_dialog import *
import util_dialog


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
        self.interfaceAddData = interface
        QDockWidget.__init__(self)
        self.setupUi(self)

        self.host = whost
        self.port = wport
        self.bdd = wbdd
        self.username = wusername
        self.psw = wpsw
# ----------------------------- ------------------ CONNEXION DES WIDGET --------------------------------------------------------

        # Fonction réinitialisation des paramètres des filtes 
        self.pb_reset.clicked.connect(self.reinitialisation)

        # Fonction pour ouvrir l'aide
        self.pb_help.clicked.connect(util_dialog.openHelp)


        # Fonction de connexion à la fenêtre additional_data_filter_dialog
        self.pb_additionalFilter.clicked.connect(self.openAddDataFilter)

        # Fonctions pour tout cocher ou tout décocher dans la CheckableComboBox contenant les sources (ccb_source)
        self.pb_check.clicked.connect(self.check_all)
        self.pb_uncheck.clicked.connect(self.uncheck_all)


        # Initialisation du nombre de sources sélectionnées
        # self.maj_lbl_sourceselectcount()
        # Fonction pour mettre à jour le nombre de sources sélectionnées quand une case est cocher ou décocher dans ccb_source
        self.ccb_source.checkedItemsChanged.connect(self.maj_lbl_sourceselectcount) # Ajout du signal

        # Fonction pour mettre à jour le nombre de sources sélectionnées quand une case est cocher ou décocher dans ccb_source
        self.lw_zonage.itemSelectionChanged.connect(self.maj_lbl_zonageparam)  # Ajout du signal

        # pour test sélection AOT
        self.pb_test_selection.clicked.connect(self.test_selection)
    


        self.lw_zonage.itemSelectionChanged.connect(self.lockZoneFilter)
        #  Pour Instancier les valeurs de la QcheckableComboBox (ccb_source) concernant les sources en fonction des valeurs via dans lw_source
        self.lw_zonage.itemSelectionChanged.connect(self.selection_typeZonage)


        # Fermer la fenêtre
        self.pb_quit.clicked.connect(self.quitter)


# ------------------------------------------------ VARIABLES GLOBALES --------------------------------------------
#  Pour Instancier la liste qui vient alimenter le QlistWidget (lw_zonage) concernant le type de zonage 
        self.lstZonage = []
        self.getTypeZonage()

#  Pour Instancier les valeurs de la QcheckableComboBox (ccb_source) concernant les sources
        # self.lw_zonage.selectedItems(self.selection_typeZonage)

# ------------------------------------------------ PARAMETRES AVANCES ----------------------------------------------------------------
# 0 - EN COURS - Ajout des valeurs de la sélection de l'état du champ "enable" (géométrie active dans géonature)
#  pour filtrer sur le champ "enable" (Géométrie active dans Géonature) avec les radio boutons  

        if self.rdb_no.isChecked() == True:
           enable = "enable IS true"

        elif self.rdb_yes.isChecked() == True : 
            enable = "enable IS NOT true"

        elif self.rdb_na.isChecked() == True :
            enable = ""


# ----------------------------- ------------------ DEFINITION DES METHODES --------------------------------------------------------
   
    # 0 - EN COURS DE DEV ----------------------------------------
    def selection_typeZonage(self):  # Filtrer les sources en fonction du/des types de zonages sélectionnés 
        lst_type = []
        if len(self.lw_zonage.selectedItems()) > 1 :
        # récupération des zonages sélectionnés de la QListWidget "lw_zonage"
            for uneSelection in self.lw_zonage.selectedItems():
                #print(uneSelection.data(Qt.UserRole))
                data = uneSelection.data(Qt.UserRole)
                id_type = data[3]
                lst_type.append(str(id_type))
            self.getSource(lst_type)
    # 0 - ----------------------------------------------------------------


    def test_selection(self):
        # lst_type = []
        # récupération des zonages sélectionnés de la QListWidget "lw_zonage"
        for uneSelection in self.lw_zonage.selectedItems():
            # print(uneSelection.text() + " AND")
            print(uneSelection.data(Qt.UserRole))
        #     data = uneSelection.data(Qt.UserRole)
        #     id_type = data[3]
        #     lst_type.append(str(id_type))
        # self.getSource(lst_type)

        # récupération des sources cochées de la QgsCheckableComboBox "ccb_source"
        for uneSelection in self.ccb_source.checkedItems():
            print(uneSelection + " AND")

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
            wsql += "(SELECT DISTINCT type_name, 'surface' as type_obj, 'ref_geo.bib_areas_types' as nom_table, id_type FROM ref_geo.bib_areas_types UNION "
            wsql +="SELECT DISTINCT type_name, 'ligne' as type_obj, 'ref_geo.bib_linears_types' as nom_table, id_type FROM ref_geo.bib_linears_types UNION "
            wsql +="SELECT DISTINCT type_name, 'point' as type_obj, 'ref_geo.bib_points_types' as nom_table, id_type FROM ref_geo.bib_points_types) as rq0 " 
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
                    item.setData(Qt.UserRole, data)
                    self.lw_zonage.addItem(item)

            db.close()

                                                            # OU
            
# ---------------  METHODE TABLE PAR TABLE : ------------

    # def getTypeZonage(self):
    #     db = QSqlDatabase.addDatabase("QPSQL", "geonature")
    #     db.setHostName(self.host)
    #     db.setPort(self.port)
    #     db.setDatabaseName(self.bdd)
    #     db.setUserName(self.username)
    #     db.setPassword(self.psw)

    #     if (not db.open()):
    #         QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
    #     else:
    #         lstZonageAreas = []
    #         wsql1 = "SELECT DISTINCT type_name, 'Surface(s)' as type_obj, 'ref_geo.bib_areas_types' as nom_table, id_type "
    #         wsql1 += "FROM ref_geo.bib_areas_types " 
    #         wsql1 += "WHERE type_name IS NOT NULL "
    #         wsql1 += "ORDER BY type_name, type_obj;"
    #         wqueryAreas = QSqlQuery(db)
    #         wqueryAreas.prepare(wsql1)
    #         if not wqueryAreas.exec_():
    #             QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wqueryAreas.lastError().text(), QMessageBox.Ok)
    #         else:
    #             while wqueryAreas.next():
    #                 lstZonageAreas.append((wqueryAreas.value(0), wqueryAreas.value(1), wqueryAreas.value(2), wqueryAreas.value(3)))
    #             for i in lstZonageAreas:
    #                 self.lw_zonage.addItem(f"{i[0]} - {i[1]}")


    #         lstZonageLinears = []
    #         wsql2 = "SELECT DISTINCT type_name, 'Ligne(s)' as type_obj, 'ref_geo.bib_areas_types' as nom_table, id_type "
    #         wsql2 += "FROM ref_geo.bib_linears_types "
    #         wsql2 += "WHERE type_name IS NOT NULL "
    #         wsql2 += "ORDER BY type_name, type_obj;"
    #         wqueryLinears = QSqlQuery(db)
    #         wqueryLinears.prepare(wsql2)
    #         if not wqueryLinears.exec_():
    #             QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wqueryLinears.lastError().text(), QMessageBox.Ok)
    #         else:
    #             while wqueryLinears.next():
    #                 lstZonageLinears.append((wqueryLinears.value(0), wqueryLinears.value(1), wqueryLinears.value(2), wqueryLinears.value(3)))
    #             for i in lstZonageLinears:
    #                 self.lw_zonage.addItem(f"{i[0]} - {i[1]}")


    #         lstZonagePoints = []
    #         wsql3 = "SELECT DISTINCT type_name, 'Point(s)' as type_obj, 'ref_geo.bib_areas_types' as nom_table, id_type "
    #         wsql3 += "FROM ref_geo.bib_points_types " 
    #         wsql3 += "WHERE type_name IS NOT NULL "
    #         wsql3 += "ORDER BY type_name, type_obj;"
    #         wqueryPoints = QSqlQuery(db)
    #         wqueryPoints.prepare(wsql3)
    #         if not wqueryPoints.exec_():
    #             QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wqueryPoints.lastError().text(), QMessageBox.Ok)
    #         else:
    #             while wqueryPoints.next():
    #                 lstZonagePoints.append((wqueryPoints.value(0), wqueryPoints.value(1), wqueryPoints.value(2), wqueryPoints.value(3)))
    #             for i in lstZonagePoints:
    #                 self.lw_zonage.addItem(f"{i[0]} - {i[1]}")



    #         db.close()


# 0 - EN COURS DE DEV --------------------------------------------------------------------------------

# Ajout des valeurs de la sélection des sources
    def getSource(self, lst_type):
        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.host)
        db.setPort(self.port)
        db.setDatabaseName(self.bdd)
        db.setUserName(self.username)
        db.setPassword(self.psw)

        if (not db.open()):
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
        else:
            wsql = "SELECT DISTINCT source FROM "
            wsql += "(SELECT DISTINCT source FROM ref_geo.l_linears "
            wsql += "UNION SELECT DISTINCT source FROM ref_geo.l_points "
            wsql += "UNION SELECT DISTINCT source FROM ref_geo.l_areas  "
            wsql += "WHERE id_type IN (" + ", ".join(lst_type)  + ")) as rq0 "
            wsql += "ORDER BY source;"
            wquery = QSqlQuery(db)
            wquery.prepare(wsql)
            if not wquery.exec_():
                QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wquery.lastError().text(), QMessageBox.Ok)
            else:
                self.ccb_source.clear()
                while wquery.next():
                    # if wquery.value(0) == '' :
                    #     wquery = "Non-renseigné"
                    # else:
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

        #Source
        self.ccb_source.deselectAllOptions()

        #Enable
        self.rdb_na.setChecked(True)

        #Filtre additionel



    def lockZoneFilter(self):
        if len(self.lw_zonage.selectedItems()) == 1:
            self.pb_filterzonage.setEnabled(True)
            self.pb_filterzonage.setStyleSheet("QPushButton:enabled { color: rgb(5, 144, 110) }")
        else:
            self.pb_filterzonage.setEnabled(False)
            self.pb_filterzonage.setStyleSheet("QPushButton:disabled { color: gray }")


    def openAddDataFilter(self):
        connexion = AddDataFilterWidget(self.interfaceAddData, self.host, self.port, self.bdd, self.username, self.psw )
        connexion.show()
        result = connexion.exec_()
        if result:
            pass

    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["refgeo"])
        event.accept()


    def quitter(self):
        self.close()