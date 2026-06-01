from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
import os, sys

from App.models.Analizador_Lexico import TablaSimbolos

def recurso_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class QAnalisisArea(QWidget):

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.tabla_simbolos = None

        layout_main = QVBoxLayout(self)

        self.btn_tabla_simbolos = QPushButton()
        self.btn_tabla_simbolos.setIcon(QIcon(recurso_path("App/recursos/Iconos/mesa.png")))
        self.btn_tabla_simbolos.setIconSize(QSize(20, 20))
        self.btn_tabla_simbolos.setFixedSize(20, 30)
        self.btn_tabla_simbolos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tabla_simbolos.setStyleSheet("QPushButton{"
                                              "background-color: #1a5f7a;"
                                              "border: none;"
                                              "border-radius: 8px;"
                                              "margin-right: 2000px;"
                                              "margin-left: 0px;"
                                              "padding: 4px;"
                                              "}"
                                              "QPushButton:hover{"
                                              "background-color: #f1c40f;"
                                              "}")
        self.btn_tabla_simbolos.setEnabled(False)
        self.btn_tabla_simbolos.setToolTip(
            "Abre la tabla de símbolos y sus subtablas"
        )
        self.btn_tabla_simbolos.clicked.connect(self.mostrar_tabla_simbolos)
        layout_main.addWidget(self.btn_tabla_simbolos)

        splitter = QSplitter(Qt.Vertical)

        panel_lexico = QWidget()
        layout_lex = QVBoxLayout(panel_lexico)

        lbl_lex = QLabel("Analizador Léxico:")
        lbl_lex.setStyleSheet("font-weight: bold; color: #1a5f7a;")

        self.txt_lexico = QPlainTextEdit()
        self.txt_lexico.setReadOnly(True)

        layout_lex.addWidget(lbl_lex)
        layout_lex.addWidget(self.txt_lexico)

        panel_sintactico = QWidget()
        layout_sin = QVBoxLayout(panel_sintactico)

        lbl_sin = QLabel("Analizador Sintáctico:")
        lbl_sin.setStyleSheet("font-weight: bold; color: #1a5f7a;")

        self.txt_sintactico = QPlainTextEdit()
        self.txt_sintactico.setReadOnly(True)

        layout_sin.addWidget(lbl_sin)
        layout_sin.addWidget(self.txt_sintactico)

        splitter.addWidget(panel_lexico)
        splitter.addWidget(panel_sintactico)
        splitter.setSizes([400, 400])

        layout_main.addWidget(splitter)

    def establecer_tabla_simbolos(self, tabla):
        self.tabla_simbolos = tabla
        self.btn_tabla_simbolos.setEnabled(bool(tabla and tabla.tablas))

    def llenar_lexico(self, cont):
        self.txt_lexico.setPlainText(cont)

    def llenar_sintactico(self, cont, color=0):
        self.txt_sintactico.setStyleSheet(
            """
                QPlainTextEdit {
                    color: Red;
                    font-size: 13px;
                }
            """
            if color
            else ""
        )
        self.txt_sintactico.setPlainText(cont)

    def mostrar_tabla_simbolos(self):
        if not self.tabla_simbolos or not self.tabla_simbolos.tablas:
            QMessageBox.information(
                self,
                "Tabla de símbolos",
                "No hay una tabla de símbolos disponible para mostrar.",
            )
            return

        dialogo = QDialog(self)
        dialogo.setWindowTitle("Tabla de símbolos")
        dialogo.resize(540, 600)

        layout = QVBoxLayout(dialogo)

        titulo = QLabel(
            f"Tabla de símbolos: {self.tabla_simbolos.nombre_tabla or 'principal'}"
        )
        titulo.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(titulo)

        arbol = QTreeWidget()
        arbol.setColumnCount(5)
        arbol.setHeaderLabels(["Componente", "Nombre", "Tipo", "Valor", "Link"])
        arbol.setAlternatingRowColors(True)
        arbol.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        arbol.header().setStretchLastSection(False)
        layout.addWidget(arbol)

        raiz = QTreeWidgetItem([
            f"Tabla de símbolos: {self.tabla_simbolos.nombre_tabla or 'principal'}",
            "",
            "",
            "",
            "",
        ])
        fuente_raiz = raiz.font(0)
        fuente_raiz.setBold(True)
        raiz.setFont(0, fuente_raiz)
        raiz.setFirstColumnSpanned(True)
        arbol.addTopLevelItem(raiz)

        self._agregar_tabla_al_arbol(raiz, self.tabla_simbolos)
        arbol.expandAll()

        dialogo.exec()

    def _crear_item_grupo(self, texto):
        item = QTreeWidgetItem([texto, "", "", "", ""])
        fuente = item.font(0)
        fuente.setBold(True)
        item.setFont(0, fuente)
        item.setFirstColumnSpanned(True)
        return item

    def _agregar_tabla_al_arbol(self, nodo_padre, tabla):
        for componente, entradas in tabla.tablas.items():
            for nombre, tipo, valor, link in entradas:
                item = QTreeWidgetItem(
                    [
                        str(componente),
                        str(nombre),
                        str(tipo),
                        str(valor),
                        "Si" if isinstance(link, TablaSimbolos) else "No",
                    ]
                )

                if isinstance(nodo_padre, QTreeWidget):
                    nodo_padre.addTopLevelItem(item)
                else:
                    nodo_padre.addChild(item)

                if isinstance(link, TablaSimbolos):
                    grupo = self._crear_item_grupo(
                        f"Subtabla de: {link.nombre_tabla or nombre}"
                    )
                    item.addChild(grupo)
                    self._agregar_tabla_al_arbol(grupo, link)
