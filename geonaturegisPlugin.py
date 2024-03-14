# -*- coding: utf-8 -*-
"""
Importations
"""


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import sys, os

from .connexion_widget import *
from .refgeo_widget import *
from .export_widget import *
from .about_widget import *

import util

class pluginGeonatGIS:
    def __init__(self, iface):
        #permet de conserver une reference vers l'interface de QGIS
        self.interface = iface

        self.host = ""
        self.port = ""
        self.bdd = ""
        self.username = ""
        self.psw = ""

        # les 5 lignes suivantes seront à supprimer quand le plugin sera fini
        self.host = "162.19.89.37"
        self.port = 5432
        self.bdd = "geonature2db"
        self.username = "lupsig2024"
        self.psw = "fdmMP8rYr!ebCQLy"

    def initGui(self):
      self.menu = QMenu(self.interface.mainWindow())
      self.menu.setObjectName("geonaturegis")
      self.menu.setTitle("Geonature - GIS")

      #Définition action Connexion
      iconCo = QIcon(os.path.dirname(__file__) + "/icons/connexion.svg")
      self.actionConnexion = QAction(iconCo, "Connexion", self.interface.mainWindow())
      self.actionConnexion.triggered.connect(self.openConnexion)

      #Multi fenêtres dockées
      self.dicoFonction = {"refgeo": [False, None], "export": [False, None]}
      #Fénêtre du référentiel géographqiue
      iconGeoRef = QIcon(os.path.dirname(__file__) + "/icons/refgeo.png")
      self.actionRefGeo = QAction(iconGeoRef, "Référentiel Géographique", self.interface.mainWindow())
      self.actionRefGeo.triggered.connect(lambda :self.ouverture("refgeo"))
      #Fenêtre des Exports
      iconExport = QIcon(os.path.dirname(__file__) + "/icons/export_g.png")
      self.actionExport = QAction(iconExport, "Export", self.interface.mainWindow())
      self.actionExport.triggered.connect(lambda :self.ouverture("export"))

      #Bouton Aide
      iconHelp = QIcon(os.path.dirname(__file__) + "/icons/help.png")
      self.actionHelp = QAction(iconHelp, "Aide", self.interface.mainWindow())
      self.actionHelp.triggered.connect(util.openHelp)

      #Bouton À propos
      iconAbout = QIcon(os.path.dirname(__file__) + "/icons/about.svg")
      self.actionAbout = QAction(iconAbout, "À propos", self.interface.mainWindow())
      self.actionAbout.triggered.connect(self.openAbout)

      #Ajout des boutons dans la barres des menus
      self.menu.addAction(self.actionConnexion)
      self.menu.addAction(self.actionRefGeo)
      self.menu.addAction(self.actionExport)
      self.menu.addSeparator()
      self.menu.addAction(self.actionHelp)
      self.menu.addAction(self.actionAbout)

      menuBar = self.interface.mainWindow().menuBar()
      menuBar.insertMenu(self.interface.firstRightStandardMenu().menuAction(), self.menu)

      self.pluginEstActif = False
      self.fenetreDockee = None
  
    def unload(self):
        self.interface.mainWindow().menuBar().removeAction(self.menu.menuAction())

    def openConnexion(self):
        connexion = ConnexionWidget(self.interface, self.psw)
        connexion.show()
        result = connexion.exec_()
        if result:
            self.host = connexion.le_host.text()
            self.port = int(connexion.le_port.text())
            self.bdd = connexion.le_bdd.text()
            self.username = connexion.le_username.text()
            self.psw = connexion.psw

    def controleFenetreOuverte(self, fonctionAOuvrir):
        for fonction, listeInfo in self.dicoFonction.items():
            if fonction != fonctionAOuvrir:
                if listeInfo[0]:
                    listeInfo[1].close()
 
    def ouverture(self, laFonction):
        self.controleFenetreOuverte(laFonction)
        if not self.dicoFonction[laFonction][0]:
            self.dicoFonction[laFonction][0] = True
            if self.dicoFonction[laFonction][1] == None:
                if laFonction == "refgeo":
                    self.dicoFonction[laFonction][1] = RefGeoWidget(self.interface, self.host, self.port, self.bdd, self.username, self.psw)
                if laFonction == "export":
                    self.dicoFonction[laFonction][1] = ExportWidget(self.interface, self.host, self.port, self.bdd, self.username, self.psw)

                self.dicoFonction[laFonction][1].fermeFenetreFonction.connect(self.surFermetureFenetreFonction)
            self.interface.addDockWidget(Qt.RightDockWidgetArea, self.dicoFonction[laFonction][1])
            self.dicoFonction[laFonction][1].show()


    def openAbout(self):
        about = AboutWidget()
        about.show()
        result = about.exec_()

    def surFermetureFenetreFonction(self, listeFonctionAppelante):
        fonctionAppelante = listeFonctionAppelante[0]
        self.dicoFonction[fonctionAppelante][1].fermeFenetreFonction.disconnect(self.surFermetureFenetreFonction)
        self.dicoFonction[fonctionAppelante][0] = False
        self.dicoFonction[fonctionAppelante][1] = None


  



    