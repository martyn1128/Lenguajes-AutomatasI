from PySide6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QSplitter, QLabel
from PySide6.QtCore import Qt


class QAnalisisArea(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = ""
        # 1. Creamos el widget "base" que será la página de la pestaña
        layout_main = QVBoxLayout(self)

        # 2. Creamos el Splitter Vertical
        splitter = QSplitter(Qt.Vertical)

        # --- PANEL LÉXICO ---
        # El splitter requiere un Widget, así que creamos un contenedor
        panel_lexico = QWidget()
        layout_lex = QVBoxLayout(panel_lexico)

        lbl_lex = QLabel("Analizador Léxico:")
        lbl_lex.setStyleSheet("font-weight: bold; color: #1a5f7a;")

        self.txt_lexico = QPlainTextEdit()
        self.txt_lexico.setReadOnly(True)  # Solo lectura para visualización

        layout_lex.addWidget(lbl_lex)
        layout_lex.addWidget(self.txt_lexico)

        # --- PANEL SINTÁCTICO ---
        panel_sintactico = QWidget()
        layout_sin = QVBoxLayout(panel_sintactico)

        lbl_sin = QLabel("Analizador Sintáctico:")
        lbl_sin.setStyleSheet("font-weight: bold; color: #1a5f7a;")

        self.txt_sintactico = QPlainTextEdit()
        self.txt_sintactico.setReadOnly(True)

        layout_sin.addWidget(lbl_sin)
        layout_sin.addWidget(self.txt_sintactico)

        # 3. Añadimos los paneles (Widgets) al Splitter
        splitter.addWidget(panel_lexico)
        splitter.addWidget(panel_sintactico)

        # Opcional: Esto hace que el splitter empiece al 50/50
        splitter.setSizes([400, 400])

        # 4. Metemos el splitter en el layout principal
        layout_main.addWidget(splitter)


    def llenar_lexico(self, cont):
        self.txt_lexico.setPlainText(cont)

    def llenar_sintactico(self, cont):
        self.txt_sintactico.setPlainText(cont)