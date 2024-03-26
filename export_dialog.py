# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from qgis.core import *
from qgis.gui import *
import qgis.utils

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

        self.pb_export.clicked.connect(self.exporter)

        self.pb_quit.clicked.connect(self.quitter)

        

        self.nom_export = ""
        self.schema = ""
        self.vue = ""
        self.srid = ""
        self.connexionSelect =[]
        self.connexionFilter = []
        self.vlayer_point = QgsVectorLayer()
        self.vlayer_ligne = QgsVectorLayer() 
        self.vlayer_poly = QgsVectorLayer()
        self.vlayer_multipoint = QgsVectorLayer()
        self.vlayer_multiligne = QgsVectorLayer()
        self.vlayer_multipoly = QgsVectorLayer()

    def openSelectExport(self):
        self.connexionSelect = SelectExportWidget(self.interfaceFenetres, self.host, self.port, self.bdd, self.username, self.psw)
        self.reinitialisation()
        # connexion.show()
        result = self.connexionSelect.exec_()
        if result:
            return self.connexionSelect.selected_export_name , self.connexionSelect.description , self.connexionSelect.selected_view_schema, self.connexionSelect.selected_view_name, self.connexionSelect.geom_field, self.connexionSelect.srid, self.connexionSelect.pk_column, self.maj_lbl_nom_export(), self.maj_lbl_description()


    
    def openFilter(self):
        self.connexionFilter = FilterWidget(self.interfaceFenetres, self.host, self.port, self.bdd, self.username, self.psw, self.connexionSelect.selected_view_schema, self.connexionSelect.selected_view_name)
        # connexion.show()
        result = self.connexionFilter.exec_()
        if result:
            return self.connexionFilter.filter_result, self.maj_lbl_filterparam()


    def maj_lbl_nom_export(self):
        # Mettre à jour le texte du label avec la description de l'export sélectionné
            self.nom_export = self.connexionSelect.selected_export_name[0]
            self.lbl_viewname.setText(self.nom_export)


    def maj_lbl_description(self):
        # Mettre à jour le texte du label avec la description de l'export sélectionné
            description = self.connexionSelect.description[0]
            self.lbl_viewdescription.setText(description)

    def maj_lbl_filterparam(self):   
            filtre = " ".join(self.connexionFilter.filter_result)
            self.lbl_filterparam.setText(f"Filtre : {filtre}")



    def executer(self, feature): # TO DO : TRIER LES TYPES DE GEOM D'UNE VUE CF Ligne 234 separer_geom()

        self.lw_typegeomresult.clear()

        self.nom_export = self.connexionSelect.selected_export_name[0]
        self.schema = self.connexionSelect.selected_view_schema[0]
        self.vue = self.connexionSelect.selected_view_name[0]
        geom_column = self.connexionSelect.geom_field[0]
        self.srid = self.connexionSelect.srid[0]
        pk_column = self.connexionSelect.pk_column[0]

        if self.connexionFilter.filter_result != [] :
            print(self.connexionFilter.filter_result)
            filter = " ".join(self.connexionFilter.filter_result)
            filter += " AND "
        else:
            filter = ""


        wuri_point = QgsDataSourceUri()
        wuri_ligne = QgsDataSourceUri()
        wuri_poly = QgsDataSourceUri()
        wuri_multipoint = QgsDataSourceUri()
        wuri_multiligne = QgsDataSourceUri()
        wuri_multipoly = QgsDataSourceUri()

        # set host name, port, database name, username and password
        # wuri.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 
        
        wuri_point.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 
        wuri_ligne.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 
        wuri_poly.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 
        wuri_multipoint.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 
        wuri_multiligne.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 
        wuri_multipoly.setConnection(self.host, str(self.port), self.bdd , self.username, self.psw) 

        if self.connexionSelect.selected_view_name != [] :
            print(self.schema)
            print(self.vue)
            print(pk_column)


            where_point = f"{filter} ST_GeometryType({geom_column}) ILIKE 'ST_Point'"
            print(where_point)
            where_ligne = f"{filter} ST_GeometryType({geom_column}) ILIKE 'ST_LineString'"
            where_poly = f"{filter} ST_GeometryType({geom_column}) ILIKE 'ST_Polygon '"
            where_multipoint = f"{filter} ST_GeometryType({geom_column}) ILIKE 'ST_MultiPoint'"
            where_multiligne = f"{filter} ST_GeometryType({geom_column}) ILIKE 'ST_MultiLineString'"
            where_multipoly = f"{filter} ST_GeometryType({geom_column}) ILIKE 'ST_MultiPolygon'"


            # set database schema, table name, geometry column and optionally
            # subset (WHERE clause)
            wuri_point.setDataSource(self.schema, self.vue, geom_column, where_point, pk_column) # 6 LIGNES ST_geometry 
            wuri_ligne.setDataSource(self.schema, self.vue, geom_column, where_ligne, pk_column)
            wuri_poly.setDataSource(self.schema, self.vue, geom_column, where_poly, pk_column)
            wuri_multipoint.setDataSource(self.schema, self.vue, geom_column, where_multipoint, pk_column)
            wuri_multiligne.setDataSource(self.schema, self.vue, geom_column, where_multiligne, pk_column)
            wuri_multipoly.setDataSource(self.schema, self.vue, geom_column, where_multipoly, pk_column)

            self.vlayer_point = QgsVectorLayer(wuri_point.uri(), f"{self.nom_export}_{self.srid}_point", "postgres")
            self.vlayer_ligne = QgsVectorLayer(wuri_ligne.uri(), f"{self.nom_export}_{self.srid}_ligne", "postgres")
            self.vlayer_poly = QgsVectorLayer(wuri_poly.uri(), f"{self.nom_export}_{self.srid}_poly", "postgres")
            self.vlayer_multipoint = QgsVectorLayer(wuri_multipoint.uri(), f"{self.nom_export}_{self.srid}_multipoint", "postgres")
            self.vlayer_multiligne = QgsVectorLayer(wuri_multiligne.uri(), f"{self.nom_export}_{self.srid}_multiligne", "postgres")
            self.vlayer_multipoly = QgsVectorLayer(wuri_multipoly.uri(), f"{self.nom_export}_{self.srid}_multipoly", "postgres")

            
            self.point = False
            self.ligne = False
            self.poly = False
            self.multipoint = False
            self.multiligne = False
            self.multipoly = False


            if self.vlayer_point.featureCount() > 0 :
                if self.vlayer_point.isValid() :
                    print(self.vlayer_point.featureCount())
                    print("vlayer valide point")
                    QMessageBox.information(self, "Information", "Couche valide !", QMessageBox.Ok)
                    QgsProject.instance().addMapLayer(self.vlayer_point, False)
                    self.point = True
                    self.lw_typegeomresult.addItem(f"Points ({self.vlayer_point.featureCount()})")
                    self.geomtype = "point"
                else:
                    QMessageBox.critical(self, "Erreur", "Couche non valide", QMessageBox.Ok)
                    print("vlayer non valid")
                    self.point = False

            if self.vlayer_ligne.featureCount() > 0 :
                if self.vlayer_ligne.isValid() :
                    print("vlayer valide ligne")
                    QMessageBox.information(self, "Information", "Couche valide !", QMessageBox.Ok)
                    QgsProject.instance().addMapLayer(self.vlayer_ligne, False)
                    self.ligne = True
                    self.lw_typegeomresult.addItem(f"Lignes ({self.vlayer_ligne.featureCount()})")
                    self.geomtype = "ligne"
       
                else:
                    QMessageBox.critical(self, "Erreur", "Couche non valide", QMessageBox.Ok)
                    print("vlayer non valid")
                    self.ligne = False
            
            if self.vlayer_poly.featureCount() > 0 :
                if self.vlayer_poly.isValid() :
                    print(self.vlayer_point.featureCount())
                    print("vlayer valide poly")
                    QMessageBox.information(self, "Information", "Couche valide !", QMessageBox.Ok)
                    QgsProject.instance().addMapLayer(self.vlayer_poly, False)
                    self.poly = True    
                    self.lw_typegeomresult.addItem(f"Polygone ({self.vlayer_poly.featureCount()})")
                    self.geomtype = "poly"

                else:
                    QMessageBox.critical(self, "Erreur", "Couche non valide", QMessageBox.Ok)
                    print("vlayer non valid")
                    self.poly = False

            if self.vlayer_multipoint.featureCount() > 0 :
                if self.vlayer_multipoint.isValid():
                    print("vlayer valide multipoint")
                    QMessageBox.information(self, "Information", "Couche valide !", QMessageBox.Ok)
                    QgsProject.instance().addMapLayer(self.vlayer_multipoint, False)
                    self.multipoint = True
                    self.lw_typegeomresult.addItem(f"MultiPoints ({self.vlayer_multipoint.featureCount()})")
                else:
                    QMessageBox.critical(self, "Erreur", "Couche non valide", QMessageBox.Ok)
                    print("vlayer non valid multipoint")
                    self.multipoint = False
                    self.geomtype = "multipoint"

            if self.vlayer_multiligne.featureCount() > 0 :
                if self.vlayer_multiligne.isValid() :
                    print("vlayer valide multiligne")
                    QMessageBox.information(self, "Information", "Couche valide !", QMessageBox.Ok)
                    QgsProject.instance().addMapLayer(self.vlayer_multiligne, False)
                    self.multiligne = True
                    self.lw_typegeomresult.addItem(f"MultiLignes ({self.vlayer_multiligne.featureCount()})")
                    self.geomtype = "multiligne"
                else:
                    QMessageBox.critical(self, "Erreur", "Couche non valide", QMessageBox.Ok)
                    print("vlayer non valid")
                    self.multiligne = False
                    
            if self.vlayer_multipoly.featureCount() > 0 :
                if self.vlayer_multipoly.isValid() and self.vlayer_point.featureCount() > 0 :
                    print("vlayer valide multipoly")
                    QMessageBox.information(self, "Information", "Couche valide !", QMessageBox.Ok)
                    QgsProject.instance().addMapLayer(self.vlayer_multipoly, False)
                    self.multipoly = True
                    self.lw_typegeomresult.addItem(f"MultiPolygones ({self.vlayer_multipoly.featureCount()})")
                    self.geomtype = "multipoly"

                else:
                    QMessageBox.critical(self, "Erreur", "Couche non valide", QMessageBox.Ok)
                    print("vlayer non valid")
                    self.multipoly = False
       
           
                
    def loadInQGIS(self): 

    
        for selection in self.lw_typegeomresult.selectedItems():

            if self.point is True :
                # self.vlayer_point = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_point")[0]# RAJOUTER TYPE GEOM
                root = QgsProject.instance().layerTreeRoot()
                noeudCouche0 = QgsLayerTreeLayer(self.vlayer_point)
                root.insertChildNode(0, noeudCouche0)
                # Zommer sur la couche ajoutée
                iface = qgis.utils.iface
                canvas = iface.mapCanvas()
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]
                canvas.setExtent(layer.extent())
                canvas.refresh()


            elif self.ligne is True :
                # self.vlayer_ligne = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_ligne")[0]# RAJOUTER TYPE GEOM
                root = QgsProject.instance().layerTreeRoot()
                noeudCouche1 = QgsLayerTreeLayer( self.vlayer_ligne)
                root.insertChildNode(0, noeudCouche1)
                # Zommer sur la couche ajoutée
                iface = qgis.utils.iface
                canvas = iface.mapCanvas()
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]
                canvas.setExtent(layer.extent())
                canvas.refresh()

            elif self.poly is True :
                # self.vlayer_poly = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_poly")[0]# RAJOUTER TYPE GEOM
                root = QgsProject.instance().layerTreeRoot()
                noeudCouche2 = QgsLayerTreeLayer(self.vlayer_poly)
                root.insertChildNode(0, noeudCouche2)
                # Zommer sur la couche ajoutée
                iface = qgis.utils.iface
                canvas = iface.mapCanvas()
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]
                canvas.setExtent(layer.extent())
                canvas.refresh()

            elif self.multipoint is True :
                # self.vlayer_multipoint = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_multipoint")[0]# RAJOUTER TYPE GEOM
                root = QgsProject.instance().layerTreeRoot()
                noeudCouche3 = QgsLayerTreeLayer(self.vlayer_multipoint)
                root.insertChildNode(0, noeudCouche3)
                # Zommer sur la couche ajoutée
                iface = qgis.utils.iface
                canvas = iface.mapCanvas()
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]
                canvas.setExtent(layer.extent())
                canvas.refresh()

            elif self.multiligne  is True :
                # self.vlayer_multiligne = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_multiligne")[0]# RAJOUTER TYPE GEOM
                root = QgsProject.instance().layerTreeRoot()
                noeudCouche4 = QgsLayerTreeLayer(self.vlayer_multiligne)
                root.insertChildNode(0, noeudCouche4)
                # Zommer sur la couche ajoutée
                iface = qgis.utils.iface
                canvas = iface.mapCanvas()
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]
                canvas.setExtent(layer.extent())
                canvas.refresh()

            elif self.multipoly is True :
                # self.vlayer_multipoly = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_multipoly")[0]# RAJOUTER TYPE GEOM
                root = QgsProject.instance().layerTreeRoot()
                noeudCouche5 = QgsLayerTreeLayer(self.vlayer_multipoly)
                root.insertChildNode(0, noeudCouche5)     
                # Zommer sur la couche ajoutée
                iface = qgis.utils.iface
                canvas = iface.mapCanvas()
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]
                canvas.setExtent(layer.extent())
                canvas.refresh()

        # root = QgsProject.instance().layerTreeRoot()
        # print(len(root.children()))
        

    def exporter(self): # TO DO : EXPORTER AU DIFFERENT FORMATS

        # ------------------  VOIR POUR NE SELECTIONNER QUE LE DOSSIER D EXPORT ----------------------------------------------  
        # LE NOM DU FICHIER SERA PAR DEFAUT : f"{self.nom_export}_{self.srid}" voir eventuellement rajouter le type de GEOM en plus
        
        # On récupère le chemin renseigné par l'utilisateur par qfw_folder
        output_dir = self.qfw_folder.filePath()
        print(output_dir)

        # On récupère le Format choisi par l'utilisateur dans la combobox cb_expformat
        selection_format = self.cb_expformat.currentText()

        for selection in self.lw_typegeomresult.selectedItems():
            if selection_format == "GeoJSON":
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]# rajouter le type de GEOM en plus + ne fonctionne que si couche dans arbre de couche 
                # layer = QgsProject.instance().mapLayers()[0]
                self.nom_export = self.nom_export.replace("|","")
                self.nom_export = self.nom_export.replace(" ","_")
                self.nom_export = self.nom_export.replace(":","")
                self.nom_export = self.nom_export.replace("*","")
                self.nom_export = self.nom_export.replace("[","")
                self.nom_export = self.nom_export.replace("]","")
               
                print(self.nom_export)
                # FOR TESTING -------------- TBD
                # output_file = "C:/FUTURE_D/LPSIG/04-PROJETS/02-PROJETS_TUTORES/PLUGIN QGIS LPO/06-PLUGIN/test_export/test.geojson"
                output_file = f"{self.nom_export}_{self.srid}.geojson"
                # output_file = "test.geojson"
                path_file = os.path.join(output_dir,output_file)
                path_file = path_file.replace("\\","/")
                print("path:", path_file)
                if os.path.exists(path_file):
                    os.remove(path_file)

                unCrs = QgsCoordinateReferenceSystem(self.srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                print(unCrs)
                error, message = QgsVectorFileWriter.writeAsVectorFormat(layer, path_file, "utf-8", unCrs, 'GeoJSON') 
                if error > 1 :
                    print("error:", error)
                    print("message:", message)
                    QMessageBox.critical(self, "Attention", "Problème dans l'exportation", QMessageBox.Ok)
                else:
                    print("L'exportation a été effectuée avec succès")
                # A FAIRE - RECUPERER LA METHODE QUI DONNE L INFORMATION DE LA BONNE ECRITURE DU FICHIER
                    QMessageBox.information(self, "Information", "L'exportation a été effectuée avec succès!", QMessageBox.Ok)


            elif selection_format == "GeoPackage":
                # layer = self.vlayer
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]# rajouter le type de GEOM en plus + ne fonctionne que si couche dans arbre de couche 
                self.nom_export = self.nom_export.replace("|","")
                self.nom_export = self.nom_export.replace(" ","_")
                self.nom_export = self.nom_export.replace(":","")
                self.nom_export = self.nom_export.replace("*","")
                self.nom_export = self.nom_export.replace("[","")
                self.nom_export = self.nom_export.replace("]","")
                print(self.nom_export)
                # FOR TESTING -------------- TBD
                # output_file = "C:/FUTURE_D/LPSIG/04-PROJETS/02-PROJETS_TUTORES/PLUGIN QGIS LPO/06-PLUGIN/test_export/test.geojson"
                output_file = f"{self.nom_export}_{self.srid}.gpkg"
                # output_file = "test.geojson"
                path_file = os.path.join(output_dir,output_file)
                path_file = path_file.replace("\\","/")
                print("path:", path_file)
                if os.path.exists(path_file):
                    os.remove(path_file)

                unCrs = QgsCoordinateReferenceSystem(self.srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                print(unCrs)
                error, message = QgsVectorFileWriter.writeAsVectorFormat(layer, path_file, "utf-8", unCrs, 'GeoPackage') 
                if error > 1 :
                    print("error:", error)
                    print("message:", message)
                    QMessageBox.critical(self, "Attention", "Problème dans l'exportation", QMessageBox.Ok)
                else:
                    print("L'exportation a été effectuée avec succès")
                # A FAIRE - RECUPERER LA METHODE QUI DONNE L INFORMATION DE LA BONNE ECRITURE DU FICHIER
                    QMessageBox.information(self, "Information", "L'exportation a été effectuée avec succès!", QMessageBox.Ok)


            elif selection_format == "CSV":
                # layer = self.vlayer
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]# rajouter le type de GEOM en plus + ne fonctionne que si couche dans arbre de couche 
                self.nom_export = self.nom_export.replace("|","")
                self.nom_export = self.nom_export.replace(" ","_")
                self.nom_export = self.nom_export.replace(":","")
                self.nom_export = self.nom_export.replace("*","")
                self.nom_export = self.nom_export.replace("[","")
                self.nom_export = self.nom_export.replace("]","")
                print(self.nom_export)
                # FOR TESTING -------------- TBD
                # output_file = "C:/FUTURE_D/LPSIG/04-PROJETS/02-PROJETS_TUTORES/PLUGIN QGIS LPO/06-PLUGIN/test_export/test.geojson"
                output_file = f"{self.nom_export}_{self.srid}.csv"
                # output_file = "test.geojson"
                path_file = os.path.join(output_dir,output_file)
                path_file = path_file.replace("\\","/")
                print("path:", path_file)
                if os.path.exists(path_file):
                    os.remove(path_file)

                unCrs = QgsCoordinateReferenceSystem(self.srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                print(unCrs)
                error, message = QgsVectorFileWriter.writeAsVectorFormat(layer, path_file, "utf-8", unCrs, 'csv') 
                if error > 1 :
                    print("error:", error)
                    print("message:", message)
                    QMessageBox.critical(self, "Attention", "Problème dans l'exportation", QMessageBox.Ok)
                else:
                    print("L'exportation a été effectuée avec succès")
                # A FAIRE - RECUPERER LA METHODE QUI DONNE L INFORMATION DE LA BONNE ECRITURE DU FICHIER
                    QMessageBox.information(self, "Information", "L'exportation a été effectuée avec succès!", QMessageBox.Ok)

            elif selection_format == "XLSX":
                # layer = self.vlayer
                layer = QgsProject.instance().mapLayersByName(f"{self.nom_export}_{self.srid}_{self.geomtype}")[0]# rajouter le type de GEOM en plus + ne fonctionne que si couche dans arbre de couche 
                self.nom_export = self.nom_export.replace("|","")
                self.nom_export = self.nom_export.replace(" ","_")
                self.nom_export = self.nom_export.replace(":","")
                self.nom_export = self.nom_export.replace("*","")
                self.nom_export = self.nom_export.replace("[","")
                self.nom_export = self.nom_export.replace("]","")
                print(self.nom_export)
                # FOR TESTING -------------- TBD
                # output_file = "C:/FUTURE_D/LPSIG/04-PROJETS/02-PROJETS_TUTORES/PLUGIN QGIS LPO/06-PLUGIN/test_export/test.geojson"
                output_file = f"{self.nom_export}_{self.srid}.xlsx"
                # output_file = "test.geojson"
                path_file = os.path.join(output_dir,output_file)
                path_file = path_file.replace("\\","/")
                print("path:", path_file)
                if os.path.exists(path_file):
                    os.remove(path_file)

                unCrs = QgsCoordinateReferenceSystem(self.srid, QgsCoordinateReferenceSystem.EpsgCrsId)
                print(unCrs)
                error, message = QgsVectorFileWriter.writeAsVectorFormat(layer, path_file, "utf-8", unCrs, 'xlsx') 
                if error > 1 :
                    print("error:", error)
                    print("message:", message)
                    QMessageBox.critical(self, "Attention", "Problème dans l'exportation", QMessageBox.Ok)
                else:
                    print("L'exportation a été effectuée avec succès")
                # A FAIRE - RECUPERER LA METHODE QUI DONNE L INFORMATION DE LA BONNE ECRITURE DU FICHIER
                    QMessageBox.information(self, "Information", "L'exportation a été effectuée avec succès!", QMessageBox.Ok)

    def reinitialisation(self):

        print('Réinitialisé !')

        #Export
        self.connexionSelect.selected_export_name = [] 
        self.connexionSelect.description = []
        self.connexionSelect.selected_view_schema = []
        self.connexionSelect.selected_view_name = []
        self.connexionSelect.geom_field = []
        self.connexionSelect.srid = []
        
        #Filtre 
        self.filter_result = []
        self.lbl_filterparam.setText("")
        self.lbl_viewdescription.setText("")
        self.lbl_viewname.setText("")

        #EXECUTER
        self.vlayer_point = QgsVectorLayer()
        self.vlayer_ligne = QgsVectorLayer() 
        self.vlayer_poly = QgsVectorLayer()
        self.vlayer_multipoint = QgsVectorLayer()
        self.vlayer_multiligne = QgsVectorLayer()
        self.vlayer_multipoly = QgsVectorLayer()

         #Type de géométrie trouvée
        self.lw_typegeomresult.clear()

    def closeEvent(self, event):
        self.fermeFenetreFonction.emit(["export"])
        event.accept()

    def quitter(self):
        self.close()
