from PySide6.QtWidgets import QApplication
import sys

from App.controllers.main_controller import Controller
from App.views.Ventana_Principal import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = Controller(window)
    window.ventana_principal.show()
    sys.exit(app.exec())
