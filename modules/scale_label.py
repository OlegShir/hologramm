from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem, QLabel
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QFont
from modules.ChKP_table import ChkpTable
from modules.massager import MSGLabel
from PyQt5.QtCore import QPropertyAnimation, QPoint



class ScaleLabel(QGraphicsTextItem):
    def __init__(self, parent=None):
        super(ScaleLabel, self).__init__(parent)
        self.setDefaultTextColor(Qt.red) # type: ignore
        self.setFont(QFont('Arial', 12))
        self.setPlainText('23232323')