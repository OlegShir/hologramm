from PyQt5.QtWidgets import QApplication, QSlider, QVBoxLayout, QWidget, QLabel, QGridLayout, QPushButton, QGraphicsView
from PyQt5.QtCore import Qt, QRect
from modules.image_analizator import ImageAnalizator
from modules.helper import help
import sys

class SliderIMG(QWidget):
    def __init__(self, parent_widget):
        super(SliderIMG, self).__init__(parent_widget)

        self.parent_widget = parent_widget
        
        self.image_analizator: ImageAnalizator = self.parent_widget.image_analizator

        layout = QGridLayout(self)

        # Создание экземпляра QSlider
        self.slider_contrast = QSlider(Qt.Horizontal)  # type: ignore
        self.slider_bright = QSlider(Qt.Horizontal) # type: ignore
        self.slider_exp = QSlider(Qt.Horizontal) # type: ignore
        self.slider_contrast_text = QLabel('Изменение контраста')
        self.slider_bright_text = QLabel('Изменение яркости')
        self.slider_exp_text = QLabel('Изменение экспозиции')
        self.bt_contrast_reset = QPushButton('Сброс')
        self.bt_bright_reset = QPushButton('Сброс')
        self.bt_exp_reset = QPushButton('Сброс')

        # Установка подсказок
        self.slider_contrast.setToolTip(help.get('slider_contrast', ""))
        self.slider_bright.setToolTip(help.get('slider_bright', ""))
        self.slider_exp.setToolTip(help.get('slider_exp', ""))
        self.bt_contrast_reset.setToolTip(help.get('bt_contrast_reset', ""))
        self.bt_bright_reset.setToolTip(help.get('bt_bright_reset', ""))
        self.bt_exp_reset.setToolTip(help.get('bt_exp_reset', ""))
  
        # Настройка диапазона и начального значения для slider_contrast
        self.slider_contrast.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.slider_contrast.setTickInterval(1)
        self.slider_contrast.setMinimum(0)
        self.slider_contrast.setMaximum(20)
        self.slider_contrast.setValue(10)

        # Настройка диапазона и начального значения для slider_bright
        self.slider_bright.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.slider_bright.setTickInterval(1)
        self.slider_bright.setMinimum(0)
        self.slider_bright.setMaximum(20)
        self.slider_bright.setValue(10)
        
        # Настройка диапазона и начального значения для slider_exp
        self.slider_exp.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.slider_exp.setTickInterval(1)
        self.slider_exp.setMinimum(0)
        self.slider_exp.setMaximum(20)
        self.slider_exp.setValue(10)

        # Добавление слота для обработки изменений значения ползунков
        self.slider_contrast.valueChanged.connect(self.slider_changed)
        self.slider_bright.valueChanged.connect(self.slider_changed)
        self.slider_exp.valueChanged.connect(self.slider_changed)

        # Добавление слота для обработки нажатия кнопки сброса
        self.bt_contrast_reset.clicked.connect(self.reset_value_contrast)
        self.bt_bright_reset.clicked.connect(self.reset_value_bright)
        self.bt_exp_reset.clicked.connect(self.reset_value_exp)
       
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

        self.set_init()

    def set_init(self) -> None:
        self.slider_exp.setValue(10)
        self.slider_bright.setValue(10)
        self.slider_contrast.setValue(10)

    def slider_changed(self):
        self.image_analizator.adjust_image(self.slider_contrast.value()/10, 
                                           self.slider_bright.value()/10, 
                                           self.slider_exp.value()/10)
        
        self.parent_widget.ampl_char.slider_changed(0)

    def reset_value_contrast(self):
         # Обработка нажатия кнопки сброса
        self.slider_contrast.setValue(10)  # Вернуть значение контраста к исходному
        self.slider_changed()

    def reset_value_bright(self):        
        self.slider_bright.setValue(10)  # Вернуть значение яркости к исходному
        self.slider_changed()

    def reset_value_exp(self):
        self.slider_exp.setValue(10)  # Вернуть значение экспозиции к исходному
        self.slider_changed()




