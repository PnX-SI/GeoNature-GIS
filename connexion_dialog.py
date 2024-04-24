from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import sys, os

from .geonaturegisPlugin import *

sys.path.append(os.path.dirname(__file__))
from .resources_rc import *

ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_connect, _ = uic.loadUiType(os.path.join(ui_path, "connect.ui"))

class ConnexionWidget(QDialog, form_connect):
    def __init__(self, iface, wpsw, pluginGeonatGIS, parent=None):
        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.psw = wpsw
        self.recupParametre()

        # Stockage de la référence à l'instance de pluginGeonatGIS
        self.pluginGeonatGIS = pluginGeonatGIS

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)



    def recupParametre(self):
        s = QSettings()
        self.le_host.setText(s.value("geonature/config/host", ""))
        self.le_port.setText(s.value("geonature/config/port", "5432"))
        self.le_bdd.setText(s.value("geonature/config/bdd", ""))
        self.le_username.setText(s.value("geonature/config/username", ""))
        self.ple_psw.setText(self.psw)

    def majParametre(self):
        s = QSettings()
        s.setValue("geonature/config/host", self.le_host.text())
        s.setValue("geonature/config/port", self.le_port.text())
        s.setValue("geonature/config/bdd", self.le_bdd.text())
        s.setValue("geonature/config/username", self.le_username.text())
        self.psw = self.ple_psw.text()

    def testCnxOk(self):
        ret = True

        db = QSqlDatabase.addDatabase("QPSQL", "geonature")
        db.setHostName(self.le_host.text())
        db.setPort(int(self.le_port.text()))
        db.setDatabaseName(self.le_bdd.text())
        db.setUserName(self.le_username.text())
        db.setPassword(self.ple_psw.text())

        if (not db.open()):
            ret = False
        else:
            db.close()

        return ret

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self.majParametre()
        if self.testCnxOk():
            QMessageBox.information(self, "Connexion", "Connexion à la base de données réussie !", QMessageBox.Ok)

            """
                ============[ Test pour savoir si le module EXPORTS est installé ]============
            """

            db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            db.setHostName(self.le_host.text())
            db.setPort(int(self.le_port.text()))
            db.setDatabaseName(self.le_bdd.text())
            db.setUserName(self.le_username.text())
            db.setPassword(self.ple_psw.text())
            db.open()

            sql = "SELECT * FROM gn_exports.t_exports LIMIT 1;"
            wquery = QSqlQuery(db)
            wquery.exec_(sql)
            wquery.prepare(sql)
            if not wquery.exec_():
                QMessageBox.warning(self, u"Module EXPORTS non-trouvé", u"Le module EXPORTS n'a pas été trouvé. Désactivation du menu EXPORTS.", QMessageBox.Ok)
                self.pluginGeonatGIS.actionExport.setEnabled(False)
            else:
                self.pluginGeonatGIS.actionExport.setEnabled(True)

            db.close()

            """
                ==============================[ FIN DU TEST ]==============================
            """

            self.pluginGeonatGIS.actionRefGeo.setEnabled(True)
            QDialog.accept(self)
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            self.pluginGeonatGIS.actionRefGeo.setEnabled(False)
            self.pluginGeonatGIS.actionExport.setEnabled(False)
