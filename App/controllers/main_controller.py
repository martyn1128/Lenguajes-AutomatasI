import shutil

from PySide6.QtCore import QMimeData, QUrl, Qt
from PySide6.QtGui import QColor, QPalette, QPixmap, QIcon
from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QApplication, QLabel, QVBoxLayout, QDialog, \
    QPushButton
import os, sys

from App.models.Analizador_Lexico import AnalizadorLexico
from App.models.Analizador_Sintactico import AnalizadorSintactico

def recurso_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Controller:
    def __init__(self, view):
        self.corta = False
        self.view = view
        self._conectar_eventos()
        self.view.ventana_principal.actionOscuro.triggered.connect(lambda: self.aplicar_estilo("oscuro.qss"))
        self.view.ventana_principal.actionClaro.triggered.connect(lambda: self.aplicar_estilo("claro.qss"))
        
    def aplicar_estilo(self, nombre_archivo):
        ruta = f"App/recursos/{nombre_archivo}"
        with open(ruta, "r", encoding="utf-8") as f:
            self.view.ventana_principal.setStyleSheet(f.read())



    def _conectar_eventos(self):
        #MENU
            #Archivo
        self.view.ventana_principal.AbrirArchivo.triggered.connect(self.abrir_archivo)
        self.view.ventana_principal.AbrirCarpeta.triggered.connect(self.abrir_carpeta)
        self.view.ventana_principal.NuevaCarpeta.triggered.connect(self.crear_nueva_carpeta)
        self.view.ventana_principal.NuevoArchivo.triggered.connect(self.crear_nuevo_archivo)
        self.view.ventana_principal.guardar.triggered.connect(self.guardar)
        self.view.ventana_principal.guardar_c.triggered.connect(self.guardar_como)
        self.view.ventana_principal.cerrar.triggered.connect(self.cerrar_2)
        self.view.ventana_principal.selec_todo.triggered.connect(self.seleccionar_todo)
        self.view.ventana_principal.deshacer.triggered.connect(self.deshacer)
        self.view.ventana_principal.rehacer.triggered.connect(self.rehacer)
        self.view.ventana_principal.a_lexico.triggered.connect(self.analizador_lexico)
        self.view.ventana_principal.a_sintactico.triggered.connect(self.analizador_sintactico)
        self.view.ventana_principal.Acerca_de.triggered.connect(self.mostrar_acerca_de)
            #Edicion
        self.view.ventana_principal.copiar.triggered.connect(self.accion_copiar)
        self.view.ventana_principal.pegar.triggered.connect(self.accion_pegar)
        self.view.ventana_principal.cortar.triggered.connect(self.cortar)



        self.view.ventana_principal.codigo.tabCloseRequested.connect(self.cerrar_pestaña)
        self.view.ventana_principal.analisis.tabCloseRequested.connect(self.cerrar_analisis)
        self.view.exploradorC.doubleClicked.connect(self.abrir_archivo_desde_arbol)
        self.view.explorador.nuevo_archivo.connect(self.crear_nuevo_archivo)
        self.view.explorador.nueva_carpeta.connect(self.crear_nueva_carpeta)
        self.view.explorador.copiar.connect(self.accion_copiar)
        self.view.explorador.pegar.connect(self.accion_pegar)
        self.view.explorador.cortar.connect(self.cortar)
        self.view.explorador.eliminar.connect(self.eliminar)
        self.view.closeEvent = self.closeEvent
        self.view.ventana_principal.closeEvent = self.closeEvent
        self.view.ventana_principal.BtnNvo.clicked.connect(self.crear_nuevo_archivo)
        self.view.ventana_principal.BtnGuardar.clicked.connect(self.guardar)
        self.view.ventana_principal.BtnEjecutar.clicked.connect(self.ejecutar)

    def closeEvent(self, event):
        # Recorremos todas las pestañas buscando asteriscos
        for i in range(self.view.ventana_principal.codigo.count()):
            editor = self.view.ventana_principal.codigo.widget(i)
            if not editor.guardado :
                # Seleccionamos la pestaña con cambios para que el usuario la vea
                self.view.ventana_principal.codigo.setCurrentIndex(i)

                resultado = self.mostrar_alerta_guardar(self.view.ventana_principal.codigo.tabText(i))

                if resultado == QMessageBox.Discard:
                    pass
                elif resultado == QMessageBox.Save:
                    if not self.guardar():
                        event.ignore()
                        return
                else:
                    event.ignore()
                    return
        return

        event.accept()

    def mostrar_alerta(self, titulo, mensaje):
        msg = QMessageBox(self.view)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec()

    def abrir_archivo(self, file_path = None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self.view, "Abrir Código", "", "Archivos (*.txt *.py);;Todos (*.*)"
            )
        if file_path:
            for i in range(self.view.ventana_principal.codigo.count()):
                editor = self.view.ventana_principal.codigo.widget(i)
                if  hasattr(editor, 'file_path') and editor.file_path == file_path:
                    self.view.ventana_principal.codigo.setCurrentIndex(i)
                    return  # Salimos porque ya está abierto
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cont = f.read()
                nombre = os.path.basename(file_path)
                self.view.crear_nueva_pestana(nombre, cont, file_path)
                self.view.crear_nuevo_analisis(nombre, ruta=file_path)
            except FileNotFoundError:
                self.mostrar_alerta("Error", "El archivo ya no existe en esa ubicación.")
            except PermissionError:
                self.mostrar_alerta("Error", "No tienes permisos para leer este archivo.")
            except UnicodeDecodeError:
                self.mostrar_alerta("Error", "El archivo no tiene un formato de texto válido (UTF-8).")
            except Exception as e:
                # Captura cualquier otro error inesperado
                self.mostrar_alerta("Error Inesperado", f"Ocurrió algo raro: {str(e)}")

    def abrir_carpeta(self):
        # 1. Abrir el explorador de archivos de Windows (solo para carpetas)
        ruta_seleccionada = QFileDialog.getExistingDirectory(
            self.view,
            "Seleccionar Carpeta de Proyecto",
            os.getcwd(),  # Carpeta donde empieza a buscar
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if ruta_seleccionada:
            ruta_padre = os.path.dirname(ruta_seleccionada)
            carpeta = os.path.basename(ruta_seleccionada)
            self.view.exploradorC.setRootIndex(self.view.explorador.modelo_archivos.index(ruta_padre))
            self.view.explorador.ocultar_carpetas(ruta_padre,self.view.exploradorC, carpeta)

    def crear_nuevo_archivo(self):
        index = self.view.exploradorC.currentIndex()

        # Si hay algo seleccionado, usamos esa ruta; si no, usamos la raíz del árbol
        if index.isValid():
            ruta_base = self.view.explorador.modelo_archivos.filePath(index)
            # Si seleccionó un archivo, subimos un nivel para obtener su carpeta
            if not self.view.explorador.modelo_archivos.isDir(index):
                ruta_base = os.path.dirname(ruta_base)
        else:
            ruta_base = self.view.explorador.ruta

        # 2. Pedir al usuario el nombre de la nueva carpeta
        nombre_archivo, ok = QInputDialog.getText(
            self.view, "Nuevo Archivo", "Introduce el nombre del Archivo:"
        )

        # 3. Si el usuario aceptó y escribió algo
        if ok and nombre_archivo:
            ruta_completa = os.path.join(ruta_base, nombre_archivo)

            try:
                # 4. Crear el archivo
                if "." in nombre_archivo:
                    try:
                        with open(ruta_completa, 'x', encoding='utf-8') :
                            pass
                    except FileExistsError:
                        self.mostrar_alerta("Error", "La carpeta ya existe.")
                else:
                    self.mostrar_alerta("Error", "Se debe especificar el tipo de archivo ej: \n ejemplo.txt")
            except Exception as e:
                self.mostrar_aleta("Error", f"No se pudo crear la carpeta: {e}")

    def crear_nueva_carpeta(self):
        index = self.view.exploradorC.currentIndex()

        # Si hay algo seleccionado, usamos esa ruta; si no, usamos la raíz del árbol
        if index.isValid():
            ruta_base = self.view.explorador.modelo_archivos.filePath(index)
            # Si seleccionó un archivo, subimos un nivel para obtener su carpeta
            if not self.view.explorador.modelo_archivos.isDir(index):
                ruta_base = os.path.dirname(ruta_base)
        else:
            ruta_base = self.view.explorador.ruta

        # 2. Pedir al usuario el nombre de la nueva carpeta
        nombre_carpeta, ok = QInputDialog.getText(
            self.view, "Nueva Carpeta", "Introduce el nombre de la carpeta:"
        )

        # 3. Si el usuario aceptó y escribió algo
        if ok and nombre_carpeta:
            ruta_completa = os.path.join(ruta_base, nombre_carpeta)

            try:
                # 4. Crear la carpeta físicamente
                if not os.path.exists(ruta_completa):
                    os.makedirs(ruta_completa)
                else:
                    self.mostrar_alerta("Error", "La carpeta ya existe.")
            except Exception as e:
                self.mostrar_aleta("Error", f"No se pudo crear la carpeta: {e}")

    def cerrar_pestaña(self, index):
        editor = self.view.ventana_principal.codigo.widget(index)
        if editor.guardado:
            self.view.ventana_principal.codigo.removeTab(index)
        else:
            res = self.mostrar_alerta_guardar(self.view.ventana_principal.codigo.tabText(index))
            if res == QMessageBox.Discard:
                self.view.ventana_principal.codigo.removeTab(index)
            elif res == QMessageBox.Save:
                self.guardar()
            else:
                return

    def cerrar_2(self):
        index = self.view.ventana_principal.codigo.currentIndex()
        for i in range(self.view.ventana_principal.analisis.count()):
            ruta = self.view.ventana_principal.analisis.tabToolTip(i)
            if ruta == self.view.ventana_principal.codigo.widget(index).file_path:
                self.view.ventana_principal.analisis.removeTab(i)
        self.cerrar_pestaña(index)

    def mostrar_alerta_guardar(self, nombre_archivo):
        # Creamos la caja de mensaje
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Cambios sin guardar")
        msg_box.setText(f"El archivo '{nombre_archivo}' ha sido modificado.")
        msg_box.setInformativeText("¿Deseas guardar los cambios antes de cerrar?")

        # Añadimos los botones estándar
        msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        # Cambiamos los textos a español (opcional)
        msg_box.button(QMessageBox.Save).setText("Guardar")
        msg_box.button(QMessageBox.Discard).setText("No guardar")
        msg_box.button(QMessageBox.Cancel).setText("Cancelar")

        # Ponemos el foco en "Guardar" por seguridad
        msg_box.setDefaultButton(QMessageBox.Save)
        msg_box.setIcon(QMessageBox.Question)

        return msg_box.exec()

    def cerrar_analisis(self, index):
        self.view.ventana_principal.analisis.removeTab(index)

    def abrir_archivo_desde_arbol(self, index):
        ruta, carpeta = self.view.explorador.ruta_arbol(index)
        if not carpeta:
            self.abrir_archivo(ruta)

    def guardar(self):
        indice = self.view.ventana_principal.codigo.currentIndex()
        editor = self.view.ventana_principal.codigo.widget(indice)
        ruta = editor.file_path

        if os.path.exists(ruta):
            self.escribir_archivo(editor.toPlainText(), ruta)
            editor.guardado = True
            nombre_codigo = self.view.ventana_principal.codigo.tabText(indice)
            if nombre_codigo.endswith("⚠️"):
                print(nombre_codigo)
                self.view.ventana_principal.codigo.setTabText(indice, nombre_codigo[:-3])
            for i in range(self.view.ventana_principal.analisis.count()):
                if self.view.ventana_principal.analisis.tabToolTip(i) == ruta:
                    nombre_analisis = self.view.ventana_principal.analisis.tabText(i)
                    if nombre_analisis.endswith("⚠️"):
                        self.view.ventana_principal.analisis.setTabText(i, nombre_analisis[:-3])
            
            return True
        else:
            return self.guardar_como()

    def guardar_como(self):
        g = False
        indice = self.view.ventana_principal.codigo.currentIndex()
        editorcodigo = self.view.ventana_principal.codigo.widget(indice)
        contenido = editorcodigo.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Seleccione la direccion donde desea guardar el archivo", os.path.join(os.path.expanduser("~"), "Documents")
        )
        if file_path:
            if "." in file_path:
                self.escribir_archivo(contenido, file_path)
                self.view.ventana_principal.codigo.removeTab(self.view.ventana_principal.codigo.currentIndex())
                self.abrir_archivo(file_path)
                editorcodigo.guardado = True
                paleta = self.view.ventana_principal.codigo.palette()
                # 2. Extraemos el color de texto estándar (WindowText)
                color_defecto = paleta.color(QPalette.ColorRole.WindowText)
                self.view.ventana_principal.codigo.tabBar().setTabTextColor(indice, color_defecto)
                g = True
            else:
                self.mostrar_alerta("Error", "Se debe especificar el tipo de archivo ej: \n ejemplo.txt")

        return g


    def escribir_archivo(self, contenido, ruta):
        try:
            with open(ruta, "w", encoding="utf-8") as a:
                a.write(contenido)
        except Exception as e:
            self.mostrar_alerta("Alo salio Mal: ",e)

    def accion_copiar(self):
        # 1. ¿El usuario está en el explorador de archivos?
        if self.view.ventana_principal.focusWidget() == self.view.exploradorC:
            index = self.view.exploradorC.currentIndex()
            if index.isValid():
                ruta = self.view.exploradorC.model().filePath(index)
                data = QMimeData()
                data.setUrls([QUrl.fromLocalFile(ruta)])
                QApplication.clipboard().setMimeData(data)

        # 2. ¿El usuario está en una pestaña de código?
        else:
            widget_actual = self.view.ventana_principal.codigo.currentWidget()
            if widget_actual:
                if self.corta:
                    widget_actual.cut()
                else:
                    widget_actual.copy()

    def accion_pegar(self):
        mime_data = QApplication.clipboard().mimeData()

        # CASO A: Pegar Archivos en el explorador
        if self.view.ventana_principal.focusWidget() == self.view.exploradorC and mime_data.hasUrls():
            self._pegar_archivo_fisico(mime_data)

        # CASO B: Pegar Texto en el editor
        else:
            widget_actual = self.view.ventana_principal.codigo.currentWidget()
            if widget_actual and mime_data.hasText():
                widget_actual.paste()

    def _pegar_archivo_fisico(self, mime_data):
        # Obtener ruta destino (carpeta seleccionada o raíz)
        index = self.view.exploradorC.currentIndex()
        dest = (self.view.exploradorC.model().filePath(index)) if index.isValid() else self.view.exploradorC.model().rootPath()
        if not os.path.isdir(dest): dest = os.path.dirname(dest)

        for url in mime_data.urls():
            origen = url.toLocalFile()
            nombre = os.path.basename(origen)
            final = os.path.join(dest, nombre)
            try:
                if self.corta:
                    shutil.move(origen, final)
                    self.corta = False
                else:
                    if os.path.isdir(origen):
                        shutil.copytree(origen, final)
                    else:
                        shutil.copy2(origen, final)
            except Exception as e:
                self.mostrar_alerta("Error: ", e)

    def eliminar(self):
        # 1. Obtener el índice y la ruta
        index = self.view.exploradorC.currentIndex()
        if not index.isValid():
            return

        ruta = self.view.explorador.modelo_archivos.filePath(index)
        nombre = self.view.explorador.modelo_archivos.fileName(index)

        # 2. Preguntar al usuario para confirmar
        respuesta = QMessageBox.question(
            self.view,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar permanentemente '{nombre}'?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(ruta):
                    shutil.rmtree(ruta)  # Borrar carpeta y su contenido
                else:
                    os.remove(ruta)  # Borrar archivo
            except Exception as e:
                self.mostrar_alerta("Error", f"No se pudo eliminar el elemento: {e}")

    def cortar(self):
        self.corta = True
        self.accion_copiar()

    def seleccionar_todo(self):
        self.view.ventana_principal.codigo.currentWidget().selectAll()
        self.view.ventana_principal.codigo.setFocus()

    def rehacer(self):
        self.view.ventana_principal.codigo.currentWidget().redo()

    def deshacer(self):
        self.view.ventana_principal.codigo.currentWidget().undo()

    def abrir_analisis(self):
        for i in range(self.view.ventana_principal.analisis.count()):
            file_path = self.view.ventana_principal.codigo.currentWidget().file_path
            if self.view.ventana_principal.analisis.tabToolTip(i) == file_path:
                self.view.ventana_principal.analisis.setCurrentIndex(i)
                return  # Salimos porque ya está abierto
        nombre = os.path.basename(file_path)
        self.view.crear_nuevo_analisis(nombre, ruta=file_path)

    def analizador_lexico(self):
        analisis = AnalizadorLexico().analizar()
        self.abrir_analisis()
        for i in range(self.view.ventana_principal.analisis.count()):
            file_path = self.view.ventana_principal.codigo.currentWidget().file_path
            if self.view.ventana_principal.analisis.tabToolTip(i) == file_path:
                self.view.ventana_principal.analisis.setCurrentIndex(i)
                self.view.ventana_principal.analisis.widget(i).llenar_lexico(analisis)
    def analizador_sintactico(self):
        analisis = AnalizadorSintactico().analizar()
        self.abrir_analisis()
        for i in range(self.view.ventana_principal.analisis.count()):
            file_path = self.view.ventana_principal.codigo.currentWidget().file_path
            if self.view.ventana_principal.analisis.tabToolTip(i) == file_path:
                self.view.ventana_principal.analisis.setCurrentIndex(i)
                self.view.ventana_principal.analisis.widget(i).llenar_sintactico(analisis)

    def ejecutar(self):
        self.analizador_lexico()
        self.analizador_sintactico()

    def mostrar_acerca_de(self):
        # 1. Crear el diálogo
        dialogo = QDialog(self.view.ventana_principal)
        dialogo.setWindowTitle("Acerca de Pyña Code")
        dialogo.setFixedSize(400, 500)

        layout = QVBoxLayout()

        # 2. Agregar Logo
        label_logo = QLabel()
        icono_temp = QIcon(recurso_path("App/recursos/Iconos/Phyña.ico"))
        label_logo.setPixmap(icono_temp.pixmap(200, 200))
        label_logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_logo)

        # 3. Agregar Texto Informativo
        label_texto = QLabel("""
    <div style='text-align: center;'>
        <h1 style='color: #cca65b;'>Pyña Code</h1>
        <p style='font-size: 12pt; color: #3c91c7'>Compilador</p>
        <hr>
        <p><b>Equipo de Desarrollo:</b></p>
        <ul style='list-style-type: none; padding: 0; text-align: left;'>
            <li style='margin-left: 60px;'>👤 <i>Luis Martin Lopez Montes</i></li>
            <li style='margin-left: 60px;'>👤 <i>Josue Sebastian Lopez Carrillo</i></li>
            <li style='margin-left: 60px;'>👤 <i>Ana Karen Zapien Valdovinos</i></li>
        </ul>
        <p style='color: #7f8c8d; font-size: 9pt; '>Version: 1.0</p>
        <p style='color: #7f8c8d; font-size: 9pt;'>2026 © Todos los derechos reservados</p>
        <p style='color: #7f8c8d; font-size: 9pt;'>Instituto Tecnológico de Jiquilpan</p>
    </div>"""
        )
        label_texto.setOpenExternalLinks(True)
        layout.addWidget(label_texto)

        # 4. Botón de cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialogo.accept)
        layout.addWidget(btn_cerrar)

        dialogo.setLayout(layout)
        dialogo.exec()  # Muestra la ventana de forma modal