from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
import os

class Controller:
    def __init__(self, view):
        self.view = view
        self._conectar_eventos()

    def _conectar_eventos(self):
        self.view.ventana_principal.AbrirArchivo.triggered.connect(self.abrir_archivo)
        self.view.ventana_principal.AbrirCarpeta.triggered.connect(self.abrir_carpeta)
        self.view.ventana_principal.NuevaCarpeta.triggered.connect(self.crear_nueva_carpeta)
        self.view.ventana_principal.NuevoArchivo.triggered.connect(self.crear_nuevo_archivo)
        self.view.ventana_principal.codigo.tabCloseRequested.connect(self.cerrar_pestaña)
        self.view.ventana_principal.analisis.tabCloseRequested.connect(self.cerrar_analisis)
        self.view.exploradorC.doubleClicked.connect(self.abrir_archivo_desde_arbol)


    def abrir_archivo(self, file_path = None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self.view, "Abrir Código", "", "Archivos (*.txt *.py);;Todos (*.*)"
            )
        if file_path:
            for i in range(self.view.ventana_principal.codigo.count()):
                editor = self.view.ventana_principal.codigo.tabText(i)
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
            ruta_base = self.view.explorador.get_ruta()

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
            ruta_base = self.view.explorador.get_ruta()

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
                    # El QFileSystemModel detectará el cambio solo,
                    # pero podemos forzar un refresco si fuera necesario.
                else:
                    self.mostrar_alerta("Error", "La carpeta ya existe.")
            except Exception as e:
                self.mostrar_aleta("Error", f"No se pudo crear la carpeta: {e}")

    def cerrar_pestaña(self, index):
        self.view.ventana_principal.codigo.removeTab(index)

    def cerrar_analisis(self, index):
        self.view.ventana_principal.analisis.removeTab(index)


    def mostrar_alerta(self, titulo, mensaje):
        msg = QMessageBox(self.view)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec()

    def abrir_archivo_desde_arbol(self, index):
        ruta, carpeta = self.view.explorador.ruta_arbol(index)
        if not carpeta:
            self.abrir_archivo(ruta)