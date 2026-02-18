from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ventana_principal = QUiLoader().load("App/ui/Ventana_Principal.ui", None)
        self.ventana_principal.setWindowTitle("Compilador")
        