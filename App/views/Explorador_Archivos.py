from PySide6.QtWidgets import QFileSystemModel, QTreeView
import os

class QExploradorArchivos:
    def __init__(self):
        super().__init__()
        self.modelo_archivos = QFileSystemModel()
        self.ruta = None

    def get_ruta(self):
        return self.ruta

    def cargar_explorador(self, ruta = None):
        if not ruta:
            ruta = os.path.join(os.path.expanduser("~"), "Documents")
            ruta = os.path.join(ruta, "Pyña-Projects")
            os.makedirs(ruta, exist_ok=True)
        self.ruta = ruta
        ruta_padre = os.path.dirname(self.ruta)
        carpeta = os.path.basename(self.ruta)


        self.modelo_archivos.setRootPath(ruta_padre)
        treeview = QTreeView()
        treeview.setMaximumSize(450, 16777215)
        treeview.setModel(self.modelo_archivos)
        treeview.setRootIndex(self.modelo_archivos.index(ruta_padre))

        # Opcional: Ocultar columnas de tamaño y fecha para que se vea limpio
        treeview.setColumnHidden(1, True)
        treeview.setColumnHidden(2, True)
        treeview.setColumnHidden(3, True)
        self.ocultar_carpetas(ruta_padre, treeview, carpeta)
        return treeview

    def ocultar_carpetas(self, ruta_padre, treeview, carpeta):
        indice_padre = self.modelo_archivos.index(ruta_padre)
        for nombre in os.listdir(ruta_padre):
            indice_a_ocultar = self.modelo_archivos.index(ruta_padre + "/" + nombre)
            if nombre != carpeta:
                # Ocultamos la fila en la vista
                # .row() nos da el número de fila que necesita setRowHidden
                treeview.setRowHidden(indice_a_ocultar.row(), indice_padre, True)
            else:
                treeview.setRowHidden(indice_a_ocultar.row(), indice_padre, False)

    def ruta_arbol(self, index):
        # Obtener la ruta del archivo clickeado        # Verificar que no sea una carpeta
        return self.modelo_archivos.filePath(index), self.modelo_archivos.isDir(index)
