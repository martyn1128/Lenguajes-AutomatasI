from PySide6.QtWidgets import QFileSystemModel, QTreeView, QMenu
from PySide6.QtCore import Qt, Signal
import os


class QExploradorArchivos(QTreeView):
    nuevo_archivo = Signal()
    nueva_carpeta = Signal()
    copiar = Signal()
    pegar = Signal()
    eliminar = Signal()
    cortar = Signal()
    def __init__(self):
        super().__init__()
        self.modelo_archivos = QFileSystemModel()
        self.ruta = None
        self.treeview = None


    def cargar_explorador(self, ruta = None):
        if not ruta:
            ruta = os.path.join(os.path.expanduser("~"), "Documents")
            ruta = os.path.join(ruta, "Pyña-Projects")
            os.makedirs(ruta, exist_ok=True)
        self.ruta = ruta
        ruta_padre = os.path.dirname(self.ruta)
        carpeta = os.path.basename(self.ruta)


        self.modelo_archivos.setRootPath(ruta_padre)
        self.treeview = QTreeView()
        self.treeview.setMaximumSize(450, 16777215)
        self.treeview.setModel(self.modelo_archivos)
        self.treeview.setRootIndex(self.modelo_archivos.index(ruta_padre))

        # Opcional: Ocultar columnas de tamaño y fecha para que se vea limpio
        self.treeview.setColumnHidden(1, True)
        self.treeview.setColumnHidden(2, True)
        self.treeview.setColumnHidden(3, True)

        #menu click derecho
        self.treeview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(self.mostrar_menu)
        self.ocultar_carpetas(ruta_padre, carpeta)
        return self.treeview

    def ocultar_carpetas(self, ruta_padre, carpeta):
        indice_padre = self.modelo_archivos.index(ruta_padre)
        for nombre in os.listdir(ruta_padre):
            indice_a_ocultar = self.modelo_archivos.index(ruta_padre + "/" + nombre)
            if nombre != carpeta:
                # Ocultamos la fila en la vista
                # .row() nos da el número de fila que necesita setRowHidden
                self.treeview.setRowHidden(indice_a_ocultar.row(), indice_padre, True)
            else:
                self.treeview.setRowHidden(indice_a_ocultar.row(), indice_padre, False)

    def ruta_arbol(self, index):
        # Obtener la ruta del archivo clickeado        # Verificar que no sea una carpeta
        return self.modelo_archivos.filePath(index), self.modelo_archivos.isDir(index)

    def mostrar_menu(self, posicion):
        # Obtener el índice del elemento donde se hizo clic
        index = self.treeview.indexAt(posicion)

        if index.isValid():
            menu = QMenu()

            #crear submenu
            submenu_nuevo = menu.addMenu("Nuevo")
            nv_arhivo = submenu_nuevo.addAction("Nuevo archivo")
            nv_carpeta = submenu_nuevo.addAction("Nueva carpeta")
            # Crear acciones
            accion_copiar = menu.addAction("Copiar")
            accion_cortar = menu.addAction("Cortar")
            accion_pegar = menu.addAction("Pegar")
            accion_borrar = menu.addAction("Eliminar")
            menu.addSeparator()

            # Ejecutar el menú en la posición del cursor
            accion = menu.exec(self.treeview.viewport().mapToGlobal(posicion))

            # Manejar la lógica de las opciones
            if accion == accion_copiar:
                self.copiar.emit()
            elif accion == accion_pegar:
                self.pegar.emit()
            elif accion == accion_cortar:
                self.cortar.emit()
            elif accion == accion_borrar:
                self.eliminar.emit()
            elif accion == nv_arhivo:
                self.nuevo_archivo.emit()
            elif accion == nv_carpeta:
                self.nueva_carpeta.emit()