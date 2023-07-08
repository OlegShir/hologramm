from PyQt5.QtWidgets import QApplication, QSlider, QVBoxLayout, QWidget, QLabel, QGridLayout, QPushButton, QGraphicsView
from PyQt5.QtCore import Qt, QRect
import sys

class SliderIMG(QWidget):
    def __init__(self, parent=None):
        super(SliderIMG, self).__init__(parent,)

        
        self.image_analizator: QGraphicsView

        layout = QGridLayout(self)

        # Создание экземпляра QSlider
        self.slider_contrast = QSlider(Qt.Horizontal)  # type: ignore
        self.slider_bright = QSlider(Qt.Horizontal) # type: ignore
        self.slider_exp = QSlider(Qt.Horizontal) # type: ignore
        self.slider_contrast_text = QLabel('Изменение контраста')
        self.slider_bright_text = QLabel('Изменение яркости')
        self.slider_exp_text = QLabel('Экспозиция')
        self.bt_contrast_reset = QPushButton('Сброс')
        self.bt_bright_reset = QPushButton('Сброс')
        self.bt_exp_reset = QPushButton('Сброс')
  
        # Настройка диапазона и начального значения для slider_contrast
        self.slider_contrast.setMinimum(-50)
        self.slider_contrast.setMaximum(50)
        self.slider_contrast.setValue(0)

        # Настройка диапазона и начального значения для slider_bright
        self.slider_bright.setMinimum(0)
        self.slider_bright.setMaximum(255)
        self.slider_bright.setValue(128)
        
        # Настройка диапазона и начального значения для slider_bright
        self.slider_exp.setMinimum(-20)
        self.slider_exp.setMaximum(20)
        self.slider_exp.setValue(0)

        # Добавление слота для обработки изменений значения ползунков
        self.slider_contrast.valueChanged.connect(self.slider_value_changed)
        self.slider_bright.valueChanged.connect(self.slider_value_changed)
        self.slider_exp.valueChanged.connect(self.slider_value_changed)
       
        # Добавление QSlider в лайаут
        layout.addWidget(self.slider_contrast_text, 0,0)
        layout.addWidget(self.slider_contrast,1,0)
        layout.addWidget(self.bt_contrast_reset,1,1)

        layout.addWidget(self.slider_bright_text, 2,0)
        layout.addWidget(self.slider_bright, 3,0)
        layout.addWidget(self.bt_bright_reset,3,1)

        layout.addWidget(self.slider_exp_text, 4,0)
        layout.addWidget(self.slider_exp, 5,0)
        layout.addWidget(self.bt_exp_reset,5,1)

    
    def set_link(self, image_analizator):
        self.image_analizator = image_analizator


    def slider_value_changed(self):
        # Обработка изменения значения яркости
        contrast_value = self.slider_contrast.value()
        bright_value = self.slider_bright.value()
        print("Новое значение ползунков: contrast =", contrast_value, "bright =", bright_value)

    def reset_value_button(self):
        pass




