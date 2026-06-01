import os
import sys
import time

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSplashScreen


def recurso_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def configurar_identidad_app():
    if sys.platform.startswith("win"):
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "LenguajeyAutomatasI.PynaCode.1"
            )
        except Exception:
            pass


if __name__ == '__main__':
    configurar_identidad_app()

    app = QApplication(sys.argv)
    app.setApplicationName("Pyña Code")
    app.setApplicationDisplayName("Pyña Code")

    icono_app = QIcon(recurso_path("App/recursos/Iconos/Phyña.ico"))
    app.setWindowIcon(icono_app)

    with open(recurso_path("App/recursos/oscuro.qss"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    splash = QSplashScreen(icono_app.pixmap(600, 600))
    splash.showMessage("Cargando......")
    splash.show()

    app.processEvents()
    time.sleep(2)

    from App.controllers.main_controller import Controller
    from App.views.Ventana_Principal import MainWindow

    window = MainWindow()
    window.setWindowIcon(icono_app)
    window.ventana_principal.setWindowIcon(icono_app)
    controller = Controller(window)
    window.resize(2000, 900)
    window.showMaximized()
    if window.windowHandle() is not None:
        window.windowHandle().setIcon(icono_app)
    splash.finish(window)
    sys.exit(app.exec())
