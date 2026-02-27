from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import QWidget, QPlainTextEdit
from PySide6.QtGui import QColor, QPainter, QTextFormat


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class QCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.guardado = True
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        # 1. QUITAR SALTOS DE LÍNEA (NoWrap)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.setStyleSheet("font-family: 'Consolas', 'Monaco', monospace; font-size: 11pt;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 1. Obtener el texto de la línea actual
            cursor = self.textCursor()
            linea = cursor.block().text()

            # 2. Contar espacios al inicio
            indentacion = len(linea) - len(linea.lstrip())
            # 3. Hacer el salto de línea normal y añadir los espacios
            #super().keyPressEvent(event)
            self.insertPlainText("\n"+" " * indentacion)
            return
        if event.key() == Qt.Key_Backtab:  # Shift + Tab
            cursor = self.textCursor()

            # 1. Miramos qué hay en la línea actual a la izquierda del cursor
            texto_linea = cursor.block().text()
            posicion_en_linea = cursor.positionInBlock()

            # Solo intentamos borrar si hay algo a la izquierda
            if posicion_en_linea > 0:
                # Tomamos la parte de la línea antes del cursor
                parte_izquierda = texto_linea[:posicion_en_linea]

                # 2. ¿Termina la parte izquierda en espacios?
                # Calculamos cuántos espacios borrar (máximo 4)
                espacios_a_borrar = 0
                for i in range(1, 5):  # Probamos borrar 1, 2, 3 o 4
                    if parte_izquierda.endswith(" " * i):
                        espacios_a_borrar = i
                    else:
                        break

                # 3. Si encontramos espacios, los borramos
                if espacios_a_borrar > 0:
                    for _ in range(espacios_a_borrar):
                        cursor.deletePreviousChar()

                # Opcional: Si el primer caracter era un Tab real (\t), lo borramos
                elif parte_izquierda.endswith("\t"):
                    cursor.deletePreviousChar()

            return  # Consumimos el evento

        if event.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
            return
        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()

            # 1. Si hay algo seleccionado, dejamos que el comportamiento normal borre la selección
            if cursor.hasSelection():
                super().keyPressEvent(event)
                return

            # 2. Verificamos qué hay a la izquierda del cursor
            texto_linea = cursor.block().text()
            posicion_en_linea = cursor.positionInBlock()

            # Tomamos la parte de la línea antes del cursor
            parte_izquierda = texto_linea[:posicion_en_linea]

            # 3. ¿La parte izquierda termina exactamente en 4 espacios?
            if parte_izquierda.endswith("    ") and parte_izquierda.strip() == "":
                # Borramos 4 veces
                for _ in range(4):
                    cursor.deletePreviousChar()
                return  # Consumimos el evento para que no borre un 5to carácter

            # 4. Si no son 4 espacios, que borre normal
            super().keyPressEvent(event)
        super().keyPressEvent(event)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 20 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()): self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)

        # Obtenemos la paleta actual del sistema
        palette = self.palette()

        # 1. Usamos el color de 'Window' o 'AlternateBase' para el fondo del margen
        # Esto hará que si el sistema es oscuro, el margen sea oscuro.
        bg_color = palette.color(palette.ColorRole.Window)
        painter.fillRect(event.rect(), bg_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                # 2. Usamos el color 'Dark' o 'PlaceholderText' para los números
                # Así siempre habrá contraste sin importar el tema.
                painter.setPen(palette.color(palette.ColorRole.PlaceholderText))

                painter.drawText(0, top, self.line_number_area.width() - 5,
                                 self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1