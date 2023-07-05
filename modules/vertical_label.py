from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QTransform, QFontMetrics
from PyQt5.QtCore import Qt, QSize

class VerticalLabel(QLabel):
    def __init__(self, text):
        super(VerticalLabel, self).__init__(text)
        self.setGeometry(0, 0, 500, 350)
        self._text = text
        self._rotation = -90
        self._padding = 5  # Отступы для текста

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font_metrics = painter.fontMetrics()
        text_height = font_metrics.height()

        painter.translate(0, self.height())
        painter.rotate(self._rotation)

        painter.drawText(
            self._padding,
            -self.width() + self._padding,
            self.height() - 2 * self._padding,
            self.width() - 2 * self._padding,
            Qt.AlignCenter,  # type: ignore
            self._text
        )

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self._text)
        text_height = font_metrics.height()
        return QSize(text_height, text_width)

    def setText(self, text):
        self._text = text
        self.update()

    def setRotation(self, rotation):
        self._rotation = rotation
        self.update()

