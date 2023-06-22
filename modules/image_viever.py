from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap


class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)
        
        # Create a scene for displaying images
        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)
        self.setGeometry(5, 30, 516, 350)
        
        # Set initial position and size values
        self.initial_pos = 0
        self.initial_size = 0
        
        # Enable zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    
    def wheelEvent(self, event):
        # Handle mouse wheel event for zooming
        delta = event.angleDelta().y()
        factor = 1.2 ** (delta / 120)
        self.scale(factor, factor)
    
    def mousePressEvent(self, event):
        # Handle mouse press event for moving the image
        if event.button() == Qt.LeftButton: # type: ignore  
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
        # Handle mouse release event

        self.initial_pos = 0
        self.initial_size = None
        super(ImageView, self).mouseReleaseEvent(event)
    
    def create_scene(self):
        # Create the scene and return it
        return self.graphics_scene

    def open_file(self, path_to_img):
        # Загрузка изображения с помощью QPixmap
        image = QPixmap(path_to_img)
        # Установка изображения в ImageView
        self.graphics_scene.addPixmap(image)
