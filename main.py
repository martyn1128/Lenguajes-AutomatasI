import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)    
    with open("App/recursos/oscuro.qss", "r") as f:
            app.setStyleSheet(f.read())
    spalsh = QSplashScreen(QPixmap("App/recursos/Iconos/Phyña.ico").scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    spalsh.showMessage("Cargando......")
    spalsh.show()

    app.processEvents()
    time.sleep(2)

    from App.controllers.main_controller import Controller
    from App.views.Ventana_Principal import MainWindow
    window = MainWindow()
    controller = Controller(window)
    window.resize(2000,900)
    window.showMaximized()
    spalsh.finish(window.ventana_principal)
    sys.exit(app.exec())
