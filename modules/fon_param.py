from PyQt5.QtWidgets import QApplication, QGroupBox, QLineEdit, QLabel, QGridLayout, QPushButton, QGraphicsView
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from modules.helper import help
from modules.image_viewer import ImageView
import sys

class FonParam(QGroupBox):
    def __init__(self, parent_widget):
        super(FonParam, self).__init__(parent_widget,)

        self.parent_widget = parent_widget
        self.image_viewer: ImageView = self.parent_widget.image_view

        self.setGeometry(280, 410, 241, 120)
        self.setTitle("Параметры фона")

        self.fon_value_label = QLabel("", self)
        self.fon_value_label.move(10, 30)

        self.fon_refresh = QPushButton(self)
        self.fon_refresh.setFixedSize(30,30)
        pixmap = QPixmap(':/btn/qt_forms/resources/refresh.png')
        self.fon_refresh.setIcon(QIcon(pixmap))
        self.fon_refresh.setIconSize(QSize(24,24))
        self.fon_refresh.move(200, 15)

        self.btn_select_fon = QPushButton("Выбрать область фона", self)
        self.btn_select_fon.setFixedSize(140,20)
        self.btn_select_fon.move(10, 60)

        self.fon_DB = QLineEdit(self)
        self.fon_DB.setAlignment(Qt.AlignRight)  # type: ignore # Установка выравнивания по правому краю
        self.fon_DB.setFixedSize(50,20)
        self.fon_DB.move(160,60)

        DB_label = QLabel("дБ", self)
        DB_label.setFixedSize(20,20)
        DB_label.move(220, 60)

        self.btn_solve_fon = QPushButton("Рассчитать значения фона", self)
        self.btn_solve_fon.setFixedSize(200,20)
        self.btn_solve_fon.move(10, 90)

        # Устанавливаем кнопку "Выбрать область фона" в режим "переключатель"
        self.btn_select_fon.setCheckable(True)
        self.btn_select_fon.setStyleSheet("QPushButton:checked { border: 1px solid red; \
                                                        background-color: #A9B9B8; }")
        
        # Устанавливаем кнопку "Обновить" в режим "переключатель"
        self.fon_refresh.setCheckable(True)
        
        # Подключаем действия
        self.btn_select_fon.clicked.connect(self.btn_select_fon_clicked)
        self.fon_refresh.clicked.connect(self.fon_refresh_clicked)
        self.btn_solve_fon.clicked.connect(self.btn_solve_fon_clicked)
        # При изменении значения фона в дБ
        self.fon_DB.textChanged.connect(self.check_fon_DB)
        # Добавляем виджеты 

        
        self.set_value(False)

    def set_init(self) -> None:
        self.setHidden(True)

    def set_init_NOT_param(self) -> None:
        """Метод выставляет параметры виджетов, когда нет значений фона"""
        self.setHidden(False)
        self.set_value(False)
        self.fon_refresh.setEnabled(False)
        self.fon_DB.setText("")
        self.btn_select_fon.setEnabled(True)
        self.btn_solve_fon.setEnabled(True)

    def set_init_OK_param(self, DB) -> None:
        """Метод выставляет параметры виджетов, когда есть значения фона"""
        self.setHidden(False)
        self.set_value(True)
        self.fon_refresh.setEnabled(True)
        self.fon_DB.setText(str(DB))
        self.fon_DB.setEnabled(False)
        self.btn_select_fon.setEnabled(False)
        self.btn_solve_fon.setEnabled(False)
        self.fon_refresh.setChecked(False)

    def fon_refresh_clicked(self) -> None:
        if self.fon_refresh.isChecked():
            # Нажата
            status = True
        else:
            # Отжата
            status = False            
       
        self.btn_select_fon.setEnabled(status)
        self.btn_solve_fon.setEnabled(status)
        self.fon_DB.setEnabled(status)

    def check_fon_DB(self, text:str) -> None:
        # Проверяем, является ли введенный текст числом
        if len(text)>0:
            if text[0] == '-':
                if len(text)>1:
                    if not self.isFloat(text):
                        self.fon_DB.setText(text[0:-1])
            else:
                if not self.isFloat(text):
                        self.fon_DB.setText(text[0:-1])


    def isFloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def set_value(self, result: bool) -> None:
        if result:
            text = f"<html>Значение фона<b> установлено</b></html>"
        else:
            text = f"<html>Значение фона<b> не установлено</b></html>"
        self.fon_value_label.setText(text)

    def btn_select_fon_clicked(self):
        if self.btn_select_fon.isChecked():
            # Нажата
            self.image_viewer.star_fon_select  = True
        else:
            # Отжата            
            self.image_viewer.star_fon_select  = False

    def btn_solve_fon_clicked(self) -> None:
        # Проверяем что метка фона поставлена на изображении
        if self.image_viewer.fon_rect not in self.image_viewer.graphics_scene.items():
            self.parent_widget.msg.set_text("Не определена область фона", color = "r")
            return
        if self.fon_DB == "" or "0":
            self.parent_widget.msg.set_text("Не введено значение фона", color = "r")
            return
        # self.parent_widget.RSA_param["Значение фона в дБ"] = float(self.fon_DB.text())
        ROI = self.image_viewer.get_ROI_fon_in_count()
        self.parent_widget.solving_fon(ROI)
        self.image_viewer.graphics_scene.removeItem(self.image_viewer.fon_rect)
        self.image_viewer.star_fon_select  = False



