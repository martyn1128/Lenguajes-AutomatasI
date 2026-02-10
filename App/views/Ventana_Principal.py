from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ventana_principal = uic.loadUi("App/ui/Ventana_Principal.ui", self)