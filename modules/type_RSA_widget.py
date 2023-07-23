from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox,QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPixmap, QIcon
from modules.constant import RSA 
import resources

class TypeRSA(QWidget):
    def __init__(self, parent_widget):
        super(TypeRSA, self).__init__(parent_widget,)
        self.parent_widget = parent_widget

        layout = QVBoxLayout(self)

        # Создание экземпляра виджетов
        # здесь отображается название используемого авиационного РСА
        self.name_type_RSA = QLabel("")
        self.name_type_RSA.setAlignment(Qt.AlignCenter) # type: ignore
        self.name_type_RSA.setStyleSheet("background-color: #b2b5b5;")
        self.btn_param = QPushButton('Ввод параметров РСА')

        # Установка размеров 
        self.name_type_RSA.setFixedSize(140,30)
        self.btn_param.setFixedSize(140,30)

        layout.addWidget(self.name_type_RSA)
        layout.setSpacing(10)  # Вертикальный отступ между виджетами
        layout.addWidget(self.btn_param)

        self.btn_param.clicked.connect(self.add_param)

        self.set_init()

    def set_init(self) -> None:
        """Метод возвращения к начальному виду"""
        # Создание хранилища введенных значений параметров
        self.param_storage:list = []
        self.name_type_RSA.setText("")
        self.btn_param.setEnabled(False)
    
    def add_param(self):
        dialog = ParameterDialog(parent_widget=self)
        dialog.exec_()

    def update_widget(self, param_storage, index_RSA):
        self.parent_widget.RSA_name = RSA[index_RSA]
        # создаем хранилище
        param = []
        self.param_storage = param_storage
        self.name_type_RSA.setText(RSA[index_RSA])
        # приводим параметры к виду для функции свертки
        int_param = [0,1,2,5,9]
        for i in range(len(self.param_storage)):
            if i in int_param:
                value = int(self.param_storage[i])
            else:
                value = float(self.param_storage[i])
            param.append(value)
        # формируем словарь
        # для реализации правильного вызова ключей для python < 3.7, подстановку осуществляем прямую 
        dict_param={"Количество комплексных отсчетов": param[0],
                    "Количество зарегистрированных импульсов": param[1],
                    "Частота дискретизации АЦП": param[2],
                    "Длина волны": param[3],
                    "Период повторения импульсов": param[4],
                    "Ширина спектра сигнала": param[5],
                    "Длительность импульса": param[6],
                    "Скорость движения носителя": param[7],
                    "Размер антенны по азимуту": param[8],
                    "Минимальная наклонная дальность": param[9],
                    "Коэффициент сжатия": param[10],
                    "Минимальное значение РЛИ": 0,
                    "Максимальное значение РЛИ": 0,
                    "Коэффициент сигнал/фон": 0,
                    "Значение фона в дБ": 0}
        
        # Вставляем значения словаря в параметры родителя
        self.parent_widget.RSA_param = dict_param
        # разблокировка кнопки "сформировать изображение"
        self.parent_widget.get_RLI.setEnabled(True)


class ParameterDialog(QDialog):
    def __init__(self, parent_widget):
        super(ParameterDialog, self).__init__(parent_widget)

        self.parent_widget = parent_widget

        self.setWindowTitle("Ввод параметров РСА")
        pixmap = QPixmap(':/ico/qt_forms/resources/RSA.png')
        self.setWindowIcon(QIcon(pixmap))

        layout = QVBoxLayout(self)

        # Создание виджета для выбора типа авиационного РСА
        self.type_RSA_label = QLabel("Тип авиационного РСА")
        # Создание виджета QComboBox
        self.combo_box = QComboBox()
        self.combo_box.addItems(RSA)
        
        # виджета для выбора типа авиационного РСА
        layout.addWidget(self.type_RSA_label)
        layout.addWidget(self.combo_box)

        self.list_param = ["Количество комплексных отсчетов", 
                           "Количество зарегистрированных импульсов", 
                           "Частота дискретизации АЦП", 
                           "Длина волны",
                           "Период повторения импульсов", 
                           "Ширина спектра сигнала", 
                           "Длительность импульса",
                           "Скорость движения носителя",
                           "Размер антенны по азимуту",
                           "Минимальная наклонная дальность",
                           "Коэффициент сжатия"]

        # Создание виджетов для ввода параметров
        self.param_labels:list = []
        self.param_edits:list = []

        for i in range(len(self.list_param)):
            param_label = QLabel(self.list_param[i])
            param_edit = QLineEdit()
            param_edit.setFixedSize(230, 20)

            self.param_labels.append(param_label)
            self.param_edits.append(param_edit)

            layout.addWidget(param_label)
            layout.addWidget(param_edit)

        # если ввод производился ранее и параметры его сохранены вставляем их в param_edits
        if self.parent_widget.param_storage:
            for i in range(len(self.parent_widget.param_storage)):
                self.param_edits[i].setText(self.parent_widget.param_storage[i])
        
        # Создание горизонтального макета для кнопок
        button_layout = QHBoxLayout()
        
        # Создание кнопок "Принять" и "Отменить"
        self.accept_button = QPushButton("Принять")
        self.cancel_button = QPushButton("Отменить")

        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Подключение сигналов к слотам
        self.accept_button.clicked.connect(self.accept_btn)
        self.cancel_button.clicked.connect(self.reject)

    def accept_btn(self) -> None:
        param_storage_str = []

        if not self.combo_box.currentIndex():
            self.parent_widget.parent_widget.msg.set_text(f'Не выбран тип РСА', color = "r")
            return
        index_RSA = self.combo_box.currentIndex()
        # Проверка на пустые значения в параметрах и значение чисел

        for i in range(len(self.param_edits)):
            text = self.param_edits[i].text()
            # Проверяем что значения являются числами
            if text != "":
                text = text.replace(",", ".", 1)
                if not text.replace(".", "", 1).isdigit():
                    self.parent_widget.parent_widget.msg.set_text(f'Не верный формат параметра "{self.list_param[i]}"', color = "r")
                    return
            else:
                self.parent_widget.parent_widget.msg.set_text(f'Пропущен параметр "{self.list_param[i]}"',color = "r")
                return
            param_storage_str.append(text)

        self.parent_widget.update_widget(param_storage_str, index_RSA)



        self.accept()


    