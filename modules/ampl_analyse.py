import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QSlider, QWidget

class ImageApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        
        # Загрузка изображения
        self.image = cv2.imread("modules/1.png", cv2.IMREAD_GRAYSCALE)
        self.display_image = self.scale_image(self.image)
        
        # Создание виджетов
        self.image_label = QLabel(self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        
        # Создание главного макета
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.slider)
        
        # Создание виджета и установка главного макета
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Привязка событий
        self.slider.valueChanged.connect(self.update_mask)
        self.keyPressEvent = self.key_press_event

        # Отображение изображения
        self.update_display_image()
        
        # Фиксированный размер окна
        self.setFixedSize(800, 600)
        
    def update_display_image(self):
        self.scale_image(self.display_image)
        height, width = self.display_image.shape[:2]
        qimage = QImage(self.display_image.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)
        
    def scale_image(self, image):
        max_width = 800
        max_height = 600
        
        height, width = image.shape[:2]
        if width > max_width or height > max_height:
            if width > height:
                scaled_width = max_width
                scaled_height = int(height * max_width / width)
            else:
                scaled_height = max_height
                scaled_width = int(width * max_height / height)
                
            scaled_image = cv2.resize(image, (scaled_width, scaled_height))
        else:
            scaled_image = image
        
        return scaled_image
        
    def zoom_in(self):
        # Реализация приближения
        self.display_image = cv2.resize(self.display_image, None, fx=1.2, fy=1.2)
        self.update_display_image()
    
    def zoom_out(self):
        # Реализация отдаления
        self.display_image = cv2.resize(self.display_image, None, fx=0.8, fy=0.8)
        self.update_display_image()
    
    def update_mask(self, value):
        threshold = value
        ret, mask = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY)
        self.display_image = cv2.bitwise_and(self.image, self.image, mask=mask)
        self.update_display_image()

    def key_press_event(self, event):
        pass
        if event.key() == Qt.Key_Plus:
            self.zoom_in()
        if event.key() == Qt.Key_Minus:
            self.zoom_out()


# Создание экземпляра приложения Qt
app = QApplication([])

# Создание главного окна приложения
window = ImageApp()
window.show()

# Запуск главного цикла приложения
app.exec_()
