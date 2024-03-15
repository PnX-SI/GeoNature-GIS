from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import  sys,os

import util_dialog

# important pour PyQt5 et gestion du fichier resources.qrc
sys.path.append(os.path.dirname(__file__))
from .resources_rc import *

ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_about, _ = uic.loadUiType(os.path.join(ui_path, "about.ui"))



class AboutWidget(QDialog, form_about):
    
    def __init__(self, interface):
        self.interface = interface
        QWidget.__init__(self)
        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets


        self.pb_quit.clicked.connect(self.quitter)



    def quitter(self):
        self.close()