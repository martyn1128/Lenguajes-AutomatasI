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
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        # 1. QUITAR SALTOS DE LÍNEA (NoWrap)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # 2. FUENTE DE PROGRAMADOR
        self.setStyleSheet("font-family: 'Consolas', 'Monaco', monospace; font-size: 11pt;")

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