from PySide6.QtWidgets import QMainWindow, QFileSystemModel
from PySide6.QtUiTools import QUiLoader
from App.views.Edition_Area import QCodeEditor
from App.views.Analisis_Area import QAnalisisArea
from App.views.Explorador_Archivos import QExploradorArchivos
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.editor = QCodeEditor()

        self.ventana_principal = QUiLoader().load("App/ui/Ventana_Principal.ui", None)
        self.ventana_principal.setWindowTitle("Pyña")

        #Explorador de archivos
        self.explorador = QExploradorArchivos()
        self.exploradorC = self.explorador.cargar_explorador()
        self.ventana_principal.treeview.addWidget(self.exploradorC)
        self.crear_nueva_pestana("Archivo 1", "", self.explorador.get_ruta())



    def crear_nueva_pestana(self, nombre, contenido, ruta):
        nuevo_editor = QCodeEditor()
        nuevo_editor.setPlainText(contenido)
        nuevo_editor.file_path = ruta
        index = self.ventana_principal.codigo.addTab(nuevo_editor, nombre)
        self.ventana_principal.codigo.setCurrentIndex(index)
        self.ventana_principal.codigo.setTabToolTip(index, ruta)

    def crear_nuevo_analisis(self, nombre, ruta, contlex = "", contsint = ""):
        nuevo_analisis = QAnalisisArea().crear_elementos_pestaña(contlex, contsint)
        nuevo_analisis.file_path = ruta
        index = self.ventana_principal.analisis.addTab(nuevo_analisis, nombre)
        self.ventana_principal.analisis.setCurrentIndex(index)
        self.ventana_principal.analisis.setTabToolTip(index, ruta)


