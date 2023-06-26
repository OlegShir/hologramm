from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPixmap
from modules.ChKP_table import ChkpTable
from modules.massager import MSGLabel
from PyQt5.QtCore import QPropertyAnimation, QPoint


class ImageAnalizator(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageAnalizator, self).__init__(parent)

        self.setEnabled(False)
        # Create a scene for displaying images
        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)
        self.setGeometry(527, 30, 516, 350)
        # ограничители масштабирования
        self.min_ratio: float
        self.max_ratio: float
        # размер изображения в px
        self.xsize_RLI_pixmap: int
        self.ysize_RLI_pixmap: int
        # инициализация ссылки обработку изображения
        self.table: ChkpTable
        # инициализация ссылки на оценку энергетики
        self.msg: MSGLabel
        # инициализация работы с метками ЧКП
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        # инициализация масштаба
        self.scale_factor: float = 1.0
        # инициализация позиция мыши и размера 
        self.initial_pos: QPoint

        # Enable zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def set_link(self, table, msg):
        self.table = table
        self.msg = msg
    
    def wheelEvent(self, event):
        # Handle mouse wheel event for zooming
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.2
        else:
            self.scale_factor /= 1.2 

        # Ограничение масштабирования
        self.scale_factor = max(min(self.scale_factor, self.max_ratio), self.min_ratio)
     
        # масштабирование РЛИ
        self.resetTransform()
        self.scale(self.scale_factor, self.scale_factor)

            

    def mousePressEvent(self, event):
        # Handle mouse press event for moving the image
        self.initial_pos = event.pos()
        super(ImageAnalizator, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        # Handle mouse move event for moving the image
        if event.buttons() == Qt.LeftButton: # type: ignore 
            
            delta = event.pos() - self.initial_pos
            target_pos = self.viewport().pos() - delta

            animation = QPropertyAnimation(self.viewport(), b"pos")
            animation.setDuration(200)  # Длительность анимации в миллисекундах
            animation.setStartValue(self.viewport().pos())
            animation.setEndValue(target_pos)
            animation.start()

            event.accept()
    
        super(ImageAnalizator, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
      
        if event.pos() == self.initial_pos and event.button() == Qt.LeftButton: # type: ignore 
            # получение координат пикселей места нажатия
            pixmap_pos = self.mapToScene(event.pos())
                

        elif event.button() == Qt.RightButton: # type: ignore
            # получение координат пикселей места нажатия
            item_pos = self.mapToScene(event.pos())


        super(ImageAnalizator, self).mouseReleaseEvent(event)

    def get_limit_ratio(self, image) -> tuple:
        # Получение размера изображения
        self.xsize_RLI_pixmap = image.size().width()
        self.ysize_RLI_pixmap = image.size().height()
        xratio = self.size().width() / image.size().width() 
        yratio = self.size().height()/ image.size().height()

        return min(xratio, yratio), max(1/xratio, 1/yratio)
        

    def open_file(self, path_to_img):
        # Загрузка изображения с помощью QPixmap
        image = QPixmap(path_to_img)
        # Установка изображения в ImageView
        self.pixmap_item.setPixmap(image)

        self.min_ratio, self.max_ratio = self.get_limit_ratio(image)

        self.setEnabled(True)


