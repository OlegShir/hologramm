from PyQt5.QtWidgets import QFrame, QSlider, QLineEdit, QWidget, QLabel, QGridLayout, QPushButton, QGraphicsView
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPixmap, QIcon
from modules.helper import help
from modules.image_analizator import ImageAnalizator
import sys
import resources

class AmplChar(QWidget):
    def __init__(self, parent_widget):
        super(AmplChar, self).__init__(parent_widget,)

        self.parent_widget = parent_widget
        self.image_analizator:ImageAnalizator = self.parent_widget.image_analizator
    
        layout = QGridLayout(self)

        # Создание экземпляра кнопок
        self.ruler = QPushButton('')
        self.ampl_line = QPushButton('')
        self.save_SAP = QPushButton('')
        
        # Установка размеров кнопок
        self.ruler.setFixedSize(64,64)
        self.ampl_line.setFixedSize(64,64)
        self.save_SAP.setFixedSize(64,64)

        # Установка подсказок
        self.save_SAP.setToolTip(help.get('save_SAP', ''))
        self.ruler.setToolTip(help.get('ruler', ''))

        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/ruler.png')
        self.ruler.setIcon(QIcon(pixmap))
        self.ruler.setIconSize(QSize(48,48))
        pixmap = QPixmap(':/btn/qt_forms/resources/ampl_line.png')
        self.ampl_line.setIcon(QIcon(pixmap))   
        self.ampl_line.setIconSize(QSize(48,48))
        pixmap = QPixmap(':/btn/qt_forms/resources/save_SAP.png')
        self.save_SAP.setIcon(QIcon(pixmap))
        self.save_SAP.setIconSize(QSize(48,48))

        # Устанавливаем кнопку в режим "переключатель"
        self.ruler.setCheckable(True)
        self.ruler.setStyleSheet("QPushButton:checked { border: 1px solid red; \
                                                        background-color: #A9B9B8; }")

         # Добавление линии
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        
        # Создаем слайдер для маски
        mask_label = QLabel("Значение маски изображения")
        self.mask_value = QLineEdit('0')
        self.mask_value.setFixedSize(64,20)
        self.mask_slider = QSlider(Qt.Horizontal)  # type: ignore
        # Настройка диапазона и начального значения для slider
        self.mask_slider.setTickPosition(QSlider.TicksAbove)  # Риски располагаются вверху от слайдера
        self.mask_slider.setTickInterval(2)
        self.mask_slider.setMinimum(0)
        self.mask_slider.setMaximum(255)

        self.count_label = QLabel("")
        self.mean_label = QLabel("")

        # Добавление кнопок в лайаут
        layout.addWidget(self.ruler, 0,0)
        layout.addWidget(self.ampl_line,0,1)
        layout.addWidget(self.save_SAP,0,2)

  
        layout.addWidget(line, 1,0,1,3)
        layout.addWidget(mask_label,2,0,1,2)
        layout.addWidget(self.mask_value, 2,2, 1,1)
        layout.addWidget(self.mask_slider,3,0,1,3)

        layout.addWidget(QLabel("Количество пикселей в маске"), 4, 0, 1, 2)
        layout.addWidget(self.count_label, 4,2,1,1)
        layout.addWidget(QLabel("Средняя яркость изображения"), 5, 0, 1, 2)
        layout.addWidget(self.mean_label, 5,2,1,1)

        self.set_init()
        
        # Добавление функций к виджетам
        self.ruler.clicked.connect(self.ruler_clicked)
        # Подключаем слот к сигналу textChanged
        self.mask_value.textChanged.connect(self.on_text_changed)
        self.mask_value.editingFinished.connect(self.edit_finish)
        self.mask_slider.valueChanged.connect(self.slider_changed)

        self.save_SAP.clicked.connect(self.save_SAP_clicked)
        


    def set_init(self) -> None:
        self.last_mask_value = 0
        self.mask_value.setText(str(self.last_mask_value))
        self.mask_slider.setValue(self.last_mask_value)


    def on_text_changed(self, text:str) -> None:
        if text == '':
            return
        if text.isdigit():
            value = int(text)
            if 0 <= value <= 255:
                self.last_mask_value = value
                self.mask_slider.setValue(value)
            else:
                self.parent_widget.msg.set_text("Введено не корректное значение", color = 'r')
                self.mask_value.setText(str(self.last_mask_value))
        else:        
            self.parent_widget.msg.set_text("Введено не корректное значение", color = 'r')
            self.mask_value.setText(str(self.last_mask_value))

    def edit_finish(self) -> None:
        if self.mask_value.text() == "":
            self.mask_value.setText(str(self.last_mask_value))

    def slider_changed(self, value) -> None:
        self.mask_value.setText(str(value))
        self.image_analizator.threshold(value)
        
    def save_SAP_clicked(self) -> None:
        self.image_analizator.save_image()
    
    def ruler_clicked(self):
        if self.ruler.isChecked():
            # Нажата
            self.image_analizator.star_ruler  = True
        else:
            # Отжата            
            self.image_analizator.star_ruler  = False
            self.image_analizator.ruler_clear()
