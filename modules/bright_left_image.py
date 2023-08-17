from PyQt5.QtWidgets import  QGroupBox, QSlider, QLabel, QGridLayout, QPushButton, QGraphicsView
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from modules.helper import help
from modules.image_viewer import ImageView

import resources

class BrightLeft(QGroupBox):
    def __init__(self, parent_widget):
        super(BrightLeft, self).__init__(parent_widget,)

        self.parent_widget = parent_widget
        self.image_viewer: ImageView = self.parent_widget.image_view

        self.setGeometry(280, 520, 241, 123)
        self.setTitle("Регулировка РЛИ")
        self.setAlignment(Qt.AlignCenter) # type: ignore

        layout = QGridLayout(self)

        # Создание экземпляра QSlider
        self.slider_contrast = QSlider(Qt.Horizontal)  # type: ignore
        self.slider_bright = QSlider(Qt.Horizontal) # type: ignore
        self.slider_contrast_text = QLabel('Изменение контраста')
        self.slider_bright_text = QLabel('Изменение яркости')
        self.bt_contrast_reset = QPushButton('Сброс')
        self.bt_bright_reset = QPushButton('Сброс')

        # Установка подсказок
        self.slider_contrast.setToolTip(help.get('slider_contrast', ""))
        self.slider_bright.setToolTip(help.get('slider_bright', ""))
        self.bt_contrast_reset.setToolTip(help.get('bt_contrast_reset', ""))
        self.bt_bright_reset.setToolTip(help.get('bt_bright_reset', ""))

        # Настройка диапазона и начального значения для slider_contrast
        self.slider_contrast.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.slider_contrast.setTickInterval(1)
        self.slider_contrast.setMinimum(0)
        self.slider_contrast.setMaximum(10)
        self.slider_contrast.setValue(5)

        # Настройка диапазона и начального значения для slider_bright
        self.slider_bright.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.slider_bright.setTickInterval(1)
        self.slider_bright.setMinimum(0)
        self.slider_bright.setMaximum(10)
        self.slider_bright.setValue(5)
        
        # # Добавление слота для обработки изменений значения ползунков
        # self.slider_contrast.valueChanged.connect(self.slider_changed)
        # self.slider_bright.valueChanged.connect(self.slider_changed)

        # # Добавление слота для обработки нажатия кнопки сброса
        # self.bt_contrast_reset.clicked.connect(self.reset_value_contrast)
        # self.bt_bright_reset.clicked.connect(self.reset_value_bright)
       
        # Добавление QSlider в лайаут
        layout.addWidget(self.slider_contrast_text, 0,0)
        layout.addWidget(self.slider_contrast,1,0)
        layout.addWidget(self.bt_contrast_reset,1,1)

        layout.addWidget(self.slider_bright_text, 2,0)
        layout.addWidget(self.slider_bright, 3,0)
        layout.addWidget(self.bt_bright_reset,3,1)

        #self.set_init()

    def set_init(self) -> None:
        self.slider_bright.setValue(10)
        self.slider_contrast.setValue(10)
        self.setHidden(True)

        