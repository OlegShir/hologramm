from PyQt5.QtWidgets import QApplication, QSlider, QVBoxLayout, QWidget, QLabel, QGridLayout, QPushButton, QGraphicsView
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPixmap, QIcon
import sys
import resources

class AmplChar(QWidget):
    def __init__(self, parent=None):
        super(AmplChar, self).__init__(parent,)
    
        layout = QGridLayout(self)

        # Создание экземпляра кнопок
        self.ruler = QPushButton('')
        self.ampl_line = QPushButton('')
        self.ampl_rect = QPushButton('')
        
        # Установка размеров кнопок
        self.ruler.setFixedSize(64,64)
        self.ampl_line.setFixedSize(64,64)
        self.ampl_rect.setFixedSize(64,64)

        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/ruler.png')
        self.ruler.setIcon(QIcon(pixmap))
        self.ruler.setIconSize(QSize(48,48))
        pixmap = QPixmap(':/btn/qt_forms/resources/ampl_line.png')
        self.ampl_line.setIcon(QIcon(pixmap))   
        self.ampl_line.setIconSize(QSize(48,48))
        pixmap = QPixmap(':/btn/qt_forms/resources/ampl_rect.png')
        self.ampl_rect.setIcon(QIcon(pixmap))
        self.ampl_rect.setIconSize(QSize(48,48))

        # Устанавливаем кнопку в режим "переключатель"
        self.ruler.setCheckable(True)
        self.ruler.setStyleSheet("QPushButton:checked { border: 1px solid red; \
                                                        background-color: #A9B9B8; }")

        # Создаем слайдер для маски
        self.mask_slider = QSlider(Qt.Horizontal)  # type: ignore
        # Настройка диапазона и начального значения для slider
        self.mask_slider.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.mask_slider.setTickInterval(2)
        self.mask_slider.setMinimum(-255)
        self.mask_slider.setMaximum(0)
        self.mask_slider.setValue(-255)

        # Добавление кнопок в лайаут
        layout.addWidget(self.ruler, 0,0)
        layout.addWidget(self.ampl_line,0,1)
        layout.addWidget(self.ampl_rect,0,2)
        layout.addWidget(self.mask_slider,1,0,1,0)

        # Добавление функций к виджетам
        self.ruler.clicked.connect(self.ruler_clicked)
        self.ruler.clicked.connect(self.ruler_clicked)
    
    def ruler_clicked(self):
        if self.ruler.isChecked():
            # Отжата
            self.image_analizator.star_ruler  = True
        else:
            # Нажата            
            self.image_analizator.star_ruler  = False
            self.image_analizator.ruler_clear()


    



    def set_link(self, image_analizator):
        self.image_analizator = image_analizator