# MANUEL ADMINISTRATEUR
>mis à jour le 26 Avril 2024

## Architecture

![ArchitectureGenerale](./img/AM_architecture_generale.jpg)

## Base de données

L’extension Geonature - GIS s’utilise obligatoirement sur une base de données Geonature.

Il s’appuie notamment sur les schémas ``ref_geo`` et ``gn_exports`` de cette même base, de la manière suivante : 

![Utilisation des données](./img/AM_Utilisation_donnees.png)

### Gestion des droits

La gestion des droits se configure uniquement depuis le SGBD. Aucun des outils proposés dans l’extension n’influence d’accès aux données contenues dans la base de données.
Pour des raisons de sécurité, il est fortement conseillé de fournir **uniquement** les droits de lecture aux utilisateurs.



## Maintenance

Les conventions de nommage des différents widgets utilisés dans le plugin sont listés dans les parties suivantes :

### Définition des acronymes utilisés

#### Boutons
Classe | Acronyme
:--- | :--- 
QDialogButtonBox | btnBox
QPushButton | pb_
Radio Button | rb_

### Items Widgets
Classe | Acronyme
:--- | :--- 
QListWidget | lw_

#### Input Widget
Classe | Acronyme
:--- | :--- 
QLineEdit | le_
Combo Box | cb_
Line | line_

#### Display Widget
Classe | Acronyme
:--- | :--- 
QLabel | lbl_

#### QGIS Custom Widgets
Classe | Acronyme
:--- | :--- 
QgsCheckableComboBox | ccb_
QgsPasswordLineEdit | ple_
QgsFileWidget | qfw_


## Charte graphique

### Palette de couleur
Code RGB | Code Hexadécimal | Fonction
:--- | :--- | :---
rgb(245, 245, 245) | #f5f5f5 | Champ/Table
rgb(5, 144, 110) | #05906e | Bouton
rgb(255, 255, 255) | #ffffff | Texte des boutons
rgb(220, 227, 231) | #dce3e7 | Fond des fenêtres flottantes
rgb(0, 85, 127) | #00557f | Bouton “exécuter” et “export”

### Style et format des boutonṡ
Font family : Arial

Font Bold : Oui

Dimension des boutons standards : 75 x 25

# Usage
Pour toute information supplémentaire sur les différents usages, merci de vous référer au [manuel utilisateur](./user_manual.md).