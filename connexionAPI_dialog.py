from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
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
form_connect, _ = uic.loadUiType(os.path.join(ui_path, "connect_wAPI.ui"))

class ConnexionAPIWidget(QDialog, form_connect):
    def __init__(self, iface, wpsw, pluginGeonatGIS, parent=None):
        QDialog.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets

        self.psw = wpsw
        self.recupParametre()

        # Stockage de la référence à l'instance de pluginGeonatGIS
        self.pluginGeonatGIS = pluginGeonatGIS

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        # Ajout du gestionnaire de requête API
        self.network_manager = QgsNetworkAccessManager()
        self.cookies = None
        self.accepted = None



    def recupParametre(self):
        s = QSettings()
        self.le_host.setText(s.value("geonature/config/APIhost", ""))
        self.le_username.setText(s.value("geonature/config/APIusername", ""))
        self.ple_psw.setText(self.psw)

    def majParametre(self):
        s = QSettings()
        s.setValue("geonature/config/APIhost", self.le_host.text())
        s.setValue("geonature/config/APIusername", self.le_username.text())
        self.psw = self.ple_psw.text()

    def testCnxOk(self):
        ret = True

        url = QUrl(self.le_host.text())
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        # Add credentials to a json
        json_data = {
            "login": self.le_username.text(),
            "password": self.ple_psw.text(),
        }
        document = QJsonDocument(json_data)
        # Post request to test credentials
        reply = self.network_manager.post(request, document.toJson())
        # Once the asynchronous request is finished, we check the password
        reply.finished.connect(lambda: self.validate_password(reply))

        if (not reply.finished.connect(lambda: self.validate_password(reply))):
            ret = False
        else:
            print("Connexion OK")

        return ret
    
    def validate_password(self, reply):
        # Only the password is validated, there is no information on the login
        # If there is an error the message WRONG PASSWORD appear.
        # Problem, if there is no connection, or the url is wrong or anything else, the same message appear
        # TO DO change error message depending on the error code
        if reply.error() != QNetworkReply.NoError:
            self.self.ple_psw.setText("")
            print(f"code: {reply.error()} message: {reply.errorString()}")
            return False
        else:
            # Create the token to connect to the API
            self.cookies = self.network_manager.cookieJar()
            return True

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self.majParametre()
        if self.testCnxOk():
            QMessageBox.information(self, "Connexion", "Connexion à la base de données réussie !", QMessageBox.Ok)

            # """
            #     ============[ Test pour savoir si le module EXPORTS est installé ]============
            # """

            # db = QSqlDatabase.addDatabase("QPSQL", "geonature")
            # db.setHostName(self.le_host.text())
            # db.setPort(int(self.le_port.text()))
            # db.setDatabaseName(self.le_bdd.text())
            # db.setUserName(self.le_username.text())
            # db.setPassword(self.ple_psw.text())
            # db.open()

            # sql = "SELECT * FROM gn_exports.t_exports LIMIT 1;"
            # wquery = QSqlQuery(db)
            # wquery.exec_(sql)
            # wquery.prepare(sql)
            # if not wquery.exec_():
            #     QMessageBox.warning(self, u"Module EXPORTS non-trouvé", u"Le module EXPORTS n'a pas été trouvé. Désactivation du menu EXPORTS.", QMessageBox.Ok)
            #     self.pluginGeonatGIS.actionExport.setEnabled(False)
            # else:
            #     self.pluginGeonatGIS.actionExport.setEnabled(True)

            # db.close()

            # """
            #     ==============================[ FIN DU TEST ]==============================
            # """

            # self.pluginGeonatGIS.actionRefGeo.setEnabled(True)
            QDialog.accept(self)
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données ...", QMessageBox.Ok)
            self.pluginGeonatGIS.actionRefGeoAPI.setEnabled(False)
            self.pluginGeonatGIS.actionExportAPI.setEnabled(False)
