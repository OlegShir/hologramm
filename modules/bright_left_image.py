from PyQt5.QtWidgets import  QGroupBox, QSlider, QLabel, QGridLayout, QPushButton, QGraphicsView, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from modules.helper import help
from modules.image_viewer import ImageView
from modules.helper import help

import resources

class BrightLeft(QGroupBox):
    def __init__(self, parent_widget):
        super(BrightLeft, self).__init__(parent_widget,)

        self.parent_widget = parent_widget
        self.image_viewer: ImageView = self.parent_widget.image_view

        self.setGeometry(280, 530, 241, 103)
        self.setTitle("Регулировка РЛИ")
        self.setAlignment(Qt.AlignCenter) # type: ignore

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Создаем первый горизонтальный слой
        horizontal_layout1 = QHBoxLayout()
        main_layout.addLayout(horizontal_layout1)


        self.bright = QLabel('')
        self.bright.setAlignment(Qt.AlignCenter)  # type: ignore # Выравнивание по центру

        # Создаем интерфейс контраста
        # Уменьшение яркости
        bright_back  = QPushButton()
        bright_back.setFixedSize(30,30)
        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/back.png')
        bright_back.setIcon(QIcon(pixmap))
        bright_back.setIconSize(QSize(24,24))
        # Подсказка
        bright_back.setToolTip(help.get('bright_back', ''))
        bright_back.clicked.connect(lambda: self.btn_bright_clicked(-0.1, bright_back))
        
        # Сброс яркости
        bright_reset  = QPushButton()
        bright_reset.setFixedSize(30,30)
        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/reset.png')
        bright_reset.setIcon(QIcon(pixmap))
        bright_reset.setIconSize(QSize(24,24))
        # Подсказка
        bright_reset.setToolTip(help.get('bright_reset', ''))
        bright_reset.clicked.connect(lambda: self.btn_bright_clicked(0, bright_reset))

        # Увеличение яркости
        bright_forward  = QPushButton()
        bright_forward.setFixedSize(30,30)
        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/forward.png')
        bright_forward.setIcon(QIcon(pixmap))
        bright_forward.setIconSize(QSize(24,24))
        # Подсказка
        bright_forward.setToolTip(help.get('bright_forward', ''))
        bright_forward.clicked.connect(lambda: self.btn_bright_clicked(0.1, bright_forward))

        horizontal_layout1.addWidget(self.bright)
        horizontal_layout1.addWidget(bright_back)
        horizontal_layout1.addWidget(bright_reset)
        horizontal_layout1.addWidget(bright_forward)
        

        # Создаем второй горизонтальный слой
        horizontal_layout2 = QHBoxLayout()
        main_layout.addLayout(horizontal_layout2)

        self.contrast = QLabel('')
        self.contrast.setAlignment(Qt.AlignCenter)  # type: ignore # Выравнивание по центру


        # Уменьшение контраста
        contrast_back  = QPushButton()
        contrast_back.setFixedSize(30,30)
        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/back.png')
        contrast_back.setIcon(QIcon(pixmap))
        contrast_back.setIconSize(QSize(24,24))
        # Подсказка
        contrast_back.setToolTip(help.get('contrast_back', ''))
        contrast_back.clicked.connect(lambda: self.btn_contract_clicked(-0.1, contrast_back))
        
        # Сброс контраста
        contrast_reset  = QPushButton()
        contrast_reset.setFixedSize(30,30)
        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/reset.png')
        contrast_reset.setIcon(QIcon(pixmap))
        contrast_reset.setIconSize(QSize(24,24))
        # Подсказка
        contrast_reset.setToolTip(help.get('contrast_reset', ''))
        contrast_reset.clicked.connect(lambda: self.btn_contract_clicked(0, contrast_reset))

        # Увеличение контраста
        contrast_forward  = QPushButton()
        contrast_forward.setFixedSize(30,30)
        # Устанавливаем изображение на кнопку
        pixmap = QPixmap(':/btn/qt_forms/resources/forward.png')
        contrast_forward.setIcon(QIcon(pixmap))
        contrast_forward.setIconSize(QSize(24,24))
        # Подсказка
        contrast_forward.setToolTip(help.get('contrast_forward', ''))
        contrast_forward.clicked.connect(lambda: self.btn_contract_clicked(0.1, contrast_forward))

        horizontal_layout2.addWidget(self.contrast)
        horizontal_layout2.addWidget(contrast_back)
        horizontal_layout2.addWidget(contrast_reset)
        horizontal_layout2.addWidget(contrast_forward)


    def set_init(self) -> None:
        self.bright_value: float = 1
        self.contrast_value: float = 1
        self.update_text()
        self.setHidden(True)

    def btn_bright_clicked(self, value, btn):
        if not self.parent_widget.blocker.status:
            self.parent_widget.msg.set_text(f'Разблокируйте изображение РЛИ', color = 'r')
            return 
        btn.setEnabled(False)
        if value == 0:
            self.bright_value = 1
        else:
            if self.bright_value == 3.0:
                self.parent_widget.msg.set_text("Установлено максимальное значение яркости РЛИ", color = 'r')
                btn.setEnabled(True)
                return
            if self.bright_value == 0.0:
                self.parent_widget.msg.set_text("Установлено минимальное значение яркости РЛИ", color = 'r')
                btn.setEnabled(True)
                return
            self.bright_value += value
        
        self.update_text()
        
        self.image_viewer.adjust_image(self.contrast_value, 
                                       self.bright_value)
        
        btn.setEnabled(True)
        
    def btn_contract_clicked(self, value, btn):
        if not self.parent_widget.blocker.status:
            self.parent_widget.msg.set_text(f'Разблокируйте изображение РЛИ', color = 'r')
            return         
        btn.setEnabled(False)
        if value == 0:
            self.contrast_value = 1
        else:
            if self.contrast_value == 3.0:
                self.parent_widget.msg.set_text("Установлено максимальное контрастности яркости РЛИ", color = 'r')
                btn.setEnabled(True)
                return
            if self.contrast_value == 0.0:
                self.parent_widget.msg.set_text("Установлено минимальное контрастности яркости РЛИ", color = 'r')
                btn.setEnabled(True)
                return
            
            self.contrast_value += value
        
        self.update_text()
        
        self.image_viewer.adjust_image(self.contrast_value, 
                                       self.bright_value)
        
        btn.setEnabled(True)
    
    def update_text(self):

        self.bright_value = round(self.bright_value, 1)
        self.contrast_value = round(self.contrast_value, 1)

        self.bright.setText(f"<html>Коэффициент <br> яркости РЛИ: <b>{self.bright_value}</b></html>")
        self.contrast.setText(f"<html>Коэффициент <br>контраста РЛИ: <b>{self.contrast_value}</b></html>")

