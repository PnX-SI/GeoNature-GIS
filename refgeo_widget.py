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
from .additional_data_filter_widget import *


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

        self.pb_reset.clicked.connect(self.reinitialisation)


        


        self.pb_additionalFilter.clicked.connect(self.openAddDataFilter)

        # pour test sélection AOT
        self.pb_test_selection.clicked.connect(self.test_selection)




        self.getTypeZonage()
        self.getSource()






    def test_selection(self):
        # récupération des zonages sélectionnés de la QListWidget "lw_zonage"
        for uneSelection in self.lw_zonage.selectedItems():
            print(uneSelection.text())

        # récupération des sources cochées de la QgsCheckableComboBox "ccb_source"
        for uneSelection in self.ccb_source.checkedItems():
            print(uneSelection)

        # récupération de toutes les sources de "ccb_source" si aucune n'est cochée
        if len(self.ccb_source.checkedItems()) == 0:
            lst_element = []
            for i in range(self.ccb_source.count()):
                lst_element.append(self.ccb_source.itemText(i))
            print("lst_element : ", lst_element)


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
            lstZonage = []
            wsql = "SELECT DISTINCT source from "
            wsql += "(SELECT DISTINCT source FROM ref_geo.l_linears UNION SELECT DISTINCT source FROM ref_geo.l_points UNION SELECT DISTINCT source FROM ref_geo.l_areas) as rq0 "
            wsql += "WHERE source IS NOT NULL "
            wsql += "ORDER BY source;"
            wquery = QSqlQuery(db)
            wquery.prepare(wsql)
            if not wquery.exec_():
                QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wquery.lastError().text(), QMessageBox.Ok)
            else:
                while wquery.next():
                    lstZonage.append(wquery.value(0))
                self.lw_zonage.addItems(lstZonage)

            db.close()






    def getSource(self):
        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.host)
        db.setPort(self.port)
        db.setDatabaseName(self.bdd)
        db.setUserName(self.username)
        db.setPassword(self.psw)

        if (not db.open()):
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
        else:
            wsql = "SELECT DISTINCT source from "
            wsql += "(SELECT DISTINCT source FROM ref_geo.l_linears UNION SELECT DISTINCT source FROM ref_geo.l_points UNION SELECT DISTINCT source FROM ref_geo.l_areas) as rq0 "
            wsql += "ORDER BY source;"
            wquery = QSqlQuery(db)
            wquery.prepare(wsql)
            if not wquery.exec_():
                QMessageBox.critical(self, u"Impossible de récupérer les types de zonage.", wquery.lastError().text(), QMessageBox.Ok)
            else:
                while wquery.next():
                    # if wquery.value(0) == '' :
                    #     wquery = "Non-renseigné"
                    # else:
                        self.ccb_source.addItemWithCheckState(str(wquery.value(0)), False, None)
                                    

            db.close()




























    def initGui(self):
        self.pb_help.clicked.connect(self.openHelp)




    def reinitialisation(self):
        print('Réinitialisé !')

        #Zonage
        self.lw_zonage.clearSelection()

        #Source
        self.ccb_source.deselectAllOptions()

        #Enable


        #Filtre additionel













    def openAddDataFilter(self):
        connexion = AddDataFilterWidget(self.interfaceAddData)
        connexion.show()
        result = connexion.exec_()
        if result:
            pass


    def openHelp(self):
        localHelp = (os.path.dirname(__file__) + "/help/user_manual_FR.pdf")
        localHelp = localHelp.replace("\\","/")
        QDesktopServices.openUrl(QUrl(localHelp))
        print(localHelp)





    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["refgeo"])
        event.accept()
