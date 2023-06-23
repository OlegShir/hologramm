from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTableWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPixmap


class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)
        
        # Create a scene for displaying images
        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)
        self.setGeometry(5, 30, 516, 350)
        # инициализация ссылки на таблицу с ЧКП
        self.table: QTableWidget

        # инициализация работы с метками ЧКП
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        self.Chkp_pixmap = QPixmap("icon.png")
        self.xsize_Chkp_pixmap = self.Chkp_pixmap.width()
        self.ysize_Chkp_pixmap = self.Chkp_pixmap.height()
        # хранитель ЧКП
        self.labels = []
                
        self.is_open_file: bool = False
        
        # Set initial position and size values 
        self.initial_pos: QPoint
        self.initial_size = 0
        
        # Enable zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def get_link_table(self, table):
        self.table = table
    
    def wheelEvent(self, event):
        # Handle mouse wheel event for zooming
        delta = event.angleDelta().y()
        factor = 1.2 ** (delta / 120)
        self.scale(factor, factor)
    
    def mousePressEvent(self, event):
        # Handle mouse press event for moving the image
        # if event.button() == Qt.LeftButton: # type: ignore  
        self.initial_pos = event.pos()
        self.initial_size = self.size()
        super(ImageView, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        # Handle mouse move event for moving the image
        if event.buttons() == Qt.LeftButton: # type: ignore  
            delta = (event.pos() - self.initial_pos)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x()) # type: ignore 
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y()) # type: ignore 
            event.accept()
        super(ImageView, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.table.rowCount():
            # Handle mouse release event
            if event.pos() == self.initial_pos and event.button() == Qt.LeftButton: # type: ignore 
                # получение координат пикселей места нажатия
                pixmap_pos = self.mapToScene(event.pos())
                # получаем элемент на который нажали - это либо само РЛИ, либо уже существующая ЧКП
                pixmap_item = self.graphics_scene.itemAt(pixmap_pos, self.transform())
                # если не нажали ЧКП
                if pixmap_item == self.pixmap_item:
                    # добавляем изображение ЧКП в сцену
                    label = self.graphics_scene.addPixmap(self.Chkp_pixmap)
                    # установка позиции ЧКП
                    label.setPos(pixmap_pos.x() - self.xsize_Chkp_pixmap/2, pixmap_pos.y() - self.xsize_Chkp_pixmap/2)
                    # добавление в список
                    self.labels.append(label)

            elif event.button() == Qt.RightButton: # type: ignore
                # получение координат пикселей места нажатия
                item_pos = self.mapToScene(event.pos())
                # получаем элемент на который нажали
                item = self.graphics_scene.itemAt(item_pos, self.transform())
                # если это ЧКП
                if item in self.labels:
                    # поиск и удаление
                    self.graphics_scene.removeItem(item)
                    self.labels.remove(item)

        super(ImageView, self).mouseReleaseEvent(event)
    
    def create_scene(self):
        # Create the scene and return it
        return self.graphics_scene

    def open_file(self, path_to_img):
        # Загрузка изображения с помощью QPixmap
        image = QPixmap(path_to_img)
        # Установка изображения в ImageView
        self.pixmap_item.setPixmap(image)
        self.is_open_file = True

