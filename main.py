from PySide6.QtWidgets import QApplication
import sys
from App.views.Ventana_Principal import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ventana_principal.show()
    sys.exit(app.exec())
