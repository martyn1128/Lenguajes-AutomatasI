import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QMainWindow, QFileSystemModel
from PySide6.QtUiTools import QUiLoader
from App.views.Edition_Area import QCodeEditor
from App.views.Analisis_Area import QAnalisisArea
from App.views.Explorador_Archivos import QExploradorArchivos
import os

def recurso_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.editor = QCodeEditor()

        ruta_ui = recurso_path("App/ui/Ventana_Principal.ui")
        self.ventana_principal = QUiLoader().load(ruta_ui, None)
        self.setWindowTitle("Pyña Code")
        self.setWindowIcon(QIcon(recurso_path("App/recursos/iconos/Phyña.ico")))
        self.ventana_principal.BtnNvo.setIcon(QIcon(recurso_path("App/recursos/iconos/file_new_22051.ico")))
        self.ventana_principal.BtnGuardar.setIcon(QIcon(recurso_path("App/recursos/iconos/save.png")))
        self.ventana_principal.BtnEjecutar.setIcon(QIcon(recurso_path("App/recursos/iconos/run.png")))
        self.setCentralWidget(self.ventana_principal)


        #Explorador de archivos
        self.explorador = QExploradorArchivos()
        self.exploradorC = self.explorador.cargar_explorador()
        self.ventana_principal.treeview.addWidget(self.exploradorC)
        self.crear_nueva_pestana("Archivo 1", "", os.path.join(self.explorador.ruta ,"Pyña-Projects"))



    def crear_nueva_pestana(self, nombre, contenido, ruta):
        nuevo_editor = QCodeEditor()
        nuevo_editor.setPlainText(contenido)
        nuevo_editor.file_path = ruta
        nuevo_editor.textChanged.connect(lambda: self.cambios(nuevo_editor))
        index = self.ventana_principal.codigo.addTab(nuevo_editor, nombre)
        self.ventana_principal.codigo.resize(1000,100)
        self.ventana_principal.codigo.setCurrentIndex(index)
        self.ventana_principal.codigo.setTabToolTip(index, ruta)

    def crear_nuevo_analisis(self, nombre, ruta, contlex = "", contsint = ""):
        nuevo_analisis = QAnalisisArea()
        nuevo_analisis.file_path = ruta
        index = self.ventana_principal.analisis.addTab(nuevo_analisis, nombre)
        self.ventana_principal.analisis.setCurrentIndex(index)
        self.ventana_principal.analisis.setTabToolTip(index, ruta)

    def cambios(self, editor):
        # Buscamos el índice del editor que emitió el cambio
        indice = self.ventana_principal.codigo.indexOf(editor)
        
        if indice != -1:
            editor.guardado = False
            nombre = self.ventana_principal.codigo.tabText(indice)
            if not nombre.endswith("⚠️"):
                self.ventana_principal.codigo.setTabText(indice, nombre + "\t⚠️")


