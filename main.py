from PySide6.QtWidgets import QApplication
import sys
from App.views.Ventana_Principal import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ventana_principal.show()
    sys.exit(app.exec())
<<<<<<< HEAD
=======

>>>>>>> 67bcf1e2882b12ed0944d30e1e35de0f4bf35977
