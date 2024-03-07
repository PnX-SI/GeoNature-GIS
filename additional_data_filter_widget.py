from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtSql import *

from qgis.core import *
from qgis.gui import *

import os


ui_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_path, "ui")
form_add_data_filter, _ = uic.loadUiType(os.path.join(ui_path, "additional_data_filter.ui"))




class AddDataFilterWidget(QDialog, form_add_data_filter):
    def __init__(self, parent=None):
        
        QWidget.__init__(self)

        self.setupUi(self) # méthode de Ui_action1_form pour construire les widgets