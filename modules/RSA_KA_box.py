from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox,QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPixmap, QIcon
from modules.file_manager import RSAKAWorker
import resources

class RSAKABOX(QWidget):
    def __init__(self, parent_widget):
        super(RSAKABOX, self).__init__(parent_widget,)
        self.parent_widget = parent_widget


        # Создание экземпляра виджетов
        self.Kp = QLabel("Kp = ", self)
        self.Kp.move(10,5)
        self.Kp_value = QLineEdit("", self)
        self.Kp_value.setFixedSize(50, 20)
        self.Kp_value.move(45,0)

        self.box = QGroupBox("Выбор космического РСА", self)
        self.box.setFixedSize(170,90)
        self.box.move(0, 30)
        layout_box = QVBoxLayout(self.box)

        self.type_RSA = QComboBox()
        self.type_RSA.setFixedHeight(30)
        self.btn_change_RSA = QPushButton("Изменить РСА")
        self.btn_change_RSA.setFixedHeight(30)

        # Добавление виджетов в коробку
        layout_box.addWidget(self.type_RSA)
        layout_box.addWidget(self.btn_change_RSA)

        self.btn_solve = QPushButton("Провести оценку", self)
        self.btn_solve.setFixedSize(150, 30)
        self.btn_solve.move(10, 125)
        

        self.Pg = QLabel("Pg = ", self)
        self.Pg.move(10, 165)
        self.Pg_value = QLabel("2322", self)
        self.Pg_value.setFixedSize(30,20)
        self.Pg_value.move(45,165)
        
        # Добавление действий
        self.Kp_value.textChanged.connect(self.on_Kp_changed)
        self.btn_change_RSA.clicked.connect(self.btn_change_RSA_clicked)
        self.btn_solve.clicked.connect(self.btn_solve_clicked)

        self.set_init()

    def refresh_list_RSAKA(self):
        self.type_RSA.clear()
        if not self.file_worker.check_file:
            self.parent_widget.msg.set_text("Не найден фаил с параметрами РСА КА", color = 'r')
        else:
            self.list_RSAKA = self.file_worker.read_type_RSAKA()
            self.type_RSA.addItems(self.list_RSAKA)
            self.type_RSA.setCurrentIndex(0)

    def set_init(self) -> None:
        self.Kp_value.setText("")
        self.Pg_value.setText("")
        self.file_worker = RSAKAWorker("RSAKA.rsa")
        self.refresh_list_RSAKA() 


    def on_Kp_changed(self, text:str) -> None:
        # Проверяем, является ли введенный текст числом
        if len(text)>0:
            if "," or "." in text:
                try:
                    text = text.replace(",", ".")
                    float(text)
                except:
                    self.Kp_value.setText(text[0:-1])
            else: 
                if not text.isdigit():
                    self.Kp_value.setText(text[0:-1])

    def btn_change_RSA_clicked(self) -> None:
        dialog = ParameterDialog(parent_widget=self)
        dialog.exec_()


    def btn_solve_clicked(self) -> None:
        """Расчет необходимой мощности РСК КА."""
        # Проверяем введенное значение Kp
        if self.Kp_value.text() == "":
            self.parent_widget.msg.set_text("Не введено значение требуемого отношения помеха/фон", color = 'r')
            return
        try:
            Kp = float(self.Kp_value.text())
        except:
            self.parent_widget.msg.set_text("Не верный формат значения требуемого отношения помеха/фон", color = 'r')
            return
        # Проверяем, что установлено значение фона
        fon_value = self.parent_widget.fon_param.fon_DB.text()
        if fon_value == "":
            self.parent_widget.msg.set_text("Не введено значение фона", color = 'r')
            return
        # Получаем тип РСА
        type_RSA = self.type_RSA.currentText()
        if type_RSA == "":
            self.parent_widget.msg.set_text("Не выбран тип космического РСА", color = 'r')
            return
        param_RSA = self.file_worker.read_param_RASKA(type_RSA)
        # получаем параметры ЧКП
        ChKP_params = self.parent_widget.table_Chkp_2.data_collector()
        if not ChKP_params:
            self.parent_widget.msg.set_text("Отсутствуют параметры САП", color = 'r')
            return
        # пересчитываем значение фона из дБ в разы
        fon_value = 10**(float(fon_value)/10)

        # Распаковка параметров
        pulse_power, KND_antenna, observation_range, size_antenna_long, size_antenna_trans, \
        effective_area_antenna, illuminated_section, pulse_duration = param_RSA

        Pf = (pulse_power*KND_antenna*fon_value*3e8*pulse_duration*illuminated_section)/(8*3.1415*(observation_range**2))
        PG = 0
        for i in range(len(ChKP_params)):
            PG = (Kp*Pf*4*3.1415*(observation_range**2)*2*ChKP_params[i][3]*ChKP_params[i][4])/(effective_area_antenna*3e8*pulse_duration*illuminated_section)
            self.Pg_value.setText(f"{PG} Вт.")  
        # получаем параметры выбранного РСА КА
        
        

class ParameterDialog(QDialog):
    def __init__(self, parent_widget):
        super(ParameterDialog, self).__init__(parent_widget)

        self.parent_widget = parent_widget
        self.file_worker: RSAKAWorker = self.parent_widget.file_worker
 
        self.setWindowTitle("Ввод параметров РСА КА ")
        pixmap = QPixmap(':/ico/qt_forms/resources/RSA.png')
        self.setWindowIcon(QIcon(pixmap))

        layout = QVBoxLayout(self)

        # Создание виджета для выбора типа авиационного РСА
        self.type_RSA_label = QLabel("Тип космического РСА")
        # Создание виджета QComboBox
        self.combo_box = QComboBox()
        self.refresh_combobox()
        self.combo_box.setEditable(True)  # Включаем режим редактирования
        self.combo_box.currentIndexChanged.connect(self.combo_box_changed)
        
        # виджета для выбора типа авиационного РСА
        layout.addWidget(self.type_RSA_label)
        layout.addWidget(self.combo_box)

        self.list_param = ["Импульсная мощность ПРД",
                           "Коэффициент направленности антенны",
                           "Дальность радиолокационного наблюдения",
                           "Размер антенны РСА продольный",
                           "Размер антенны РСА поперечный",
                           "Эффективная площадь антенны РСА",
                           "Участок, засвечиваемый диаграммой направленности",
                           "Длительность зондирующего импульса"]

        # Создание виджетов для ввода параметров
        self.param_edits:list = []

        for i in range(len(self.list_param)):
            param_label = QLabel(self.list_param[i])
            param_edit = QLineEdit()
            param_edit.setFixedSize(300, 20)

            self.param_edits.append(param_edit)

            layout.addWidget(param_label)
            layout.addWidget(param_edit)

        # Создание горизонтального макета для кнопок
        button_layout = QHBoxLayout()
        
        # Создание кнопок "Сохранить", "Удалить", и "Отменить"
        self.save_RSA_button = QPushButton("Сохранить")
        self.del_button = QPushButton("Удалить")
        self.cancel_button = QPushButton("Отменить")

        button_layout.addWidget(self.save_RSA_button)
        button_layout.addWidget(self.del_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Подключение сигналов к слотам
        self.save_RSA_button.clicked.connect(self.save_btn)
        self.del_button.clicked.connect(self.del_btn)
        self.cancel_button.clicked.connect(self.reject)

        self.set_value(self.parent_widget.type_RSA.currentText())

    def refresh_combobox(self):
        self.combo_box.clear()
        self.list_RSAKA = self.parent_widget.list_RSAKA
        self.combo_box.addItems(self.list_RSAKA)

    def combo_box_changed(self, index) -> None:
        if index < 0:
            index = 0
        self.set_value(self.list_RSAKA[index])
        
    def set_value(self, type_RSA:str = '') -> None:
        self.combo_box.setCurrentText(type_RSA)
        if type_RSA != '':
            get_value = self.file_worker.read_param_RASKA(type_RSA)
        else:
            get_value = [""]*len(self.param_edits)
        count = 0
        for param in self.param_edits:
            param.setText(str(get_value[count]))
            count += 1
    

    def save_btn(self) -> None:

        # Проверка на пустые значения в параметрах и значение чисел
        param_storage = []
        for i in range(len(self.param_edits)):
            text = self.param_edits[i].text()
            # Проверяем что значения являются числами
            if text != "":
                text = text.replace(",", ".", 1)
                try:
                    int(text)
                except:
                    try:
                        float(text)
                    except:
                        self.parent_widget.parent_widget.msg.set_text(f'Не верный формат параметра "{self.list_param[i]}"', color = "r")
                        return
            else:
                self.parent_widget.parent_widget.msg.set_text(f'Пропущен параметр "{self.list_param[i]}"',color = "r")
                return
            param_storage.append(float(text))

        # Проверяем наличие изменения в списке
        type_RSA = self.combo_box.currentText()
        if type_RSA == "":
            self.parent_widget.parent_widget.msg.set_text(f'Не выбран тип космического РСА',color = "r")
        if type_RSA in self.list_RSAKA:
            get_value = self.file_worker.read_param_RASKA(type_RSA)
            if get_value != param_storage:
                dialog = CustomDialog(f"Вы действительно хотите перезаписать параметры {type_RSA}?    ", self, btn=2)
                result = dialog.exec_()
                if not result:
                    # Изменяем параметры РСА в файле
                    return
        # Дописываем параметры в фаил
        self.file_worker.write_RSAKA(type_RSA, param_storage)
        self.parent_widget.refresh_list_RSAKA()
        self.parent_widget.type_RSA.setCurrentText(type_RSA)

        self.accept()

    def del_btn(self) -> None:
        type_RSA = self.combo_box.currentText()
        if not type_RSA in self.list_RSAKA:
            dialog = CustomDialog(f"Данного тита РСА не существует!    ", self)
            dialog.exec_()
            return
        self.file_worker.delete_RSAKA(type_RSA)
        self.parent_widget.refresh_list_RSAKA()
        self.refresh_combobox()
    
class CustomDialog(QMessageBox):
    def __init__(self, text: str, parent=None, btn:int = 1):
        super().__init__(parent)
        self.setWindowTitle("Диалоговое окно")
        self.setText(text)
        
        if btn == 2:
            self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            self.setIcon(QMessageBox.Question)

        else:
            self.setStandardButtons(QMessageBox.Ok)

    def exec_(self):
        result = super().exec_()
        if result == QMessageBox.Ok:
            return True
        else:
            return False









"""




class RSAKA():
    def __init__(self, RSA_KA_Param) -> None:
        self.RSA_KA_Param: list = RSA_KA_Param
        self.get_init_param()

    def get_init_param(self) -> None:
        pulse_power, KND_antenna, observation_range, size_antenna_long, size_antenna_trans, \
        effective_area_antenna, illuminated_section, pulse_duration = self.RSA_KA_Param

        self.pulse_power = pulse_power
        self.KND_antenna = convert_Db_to_times(KND_antenna)
        self.observation_range = observation_range
        self.size_antenna_long = size_antenna_long
        self.size_antenna_trans = size_antenna_trans
        self.effective_area_antenna = effective_area_antenna
        self.illuminated_section = illuminated_section
        self.pulse_duration = pulse_duration

    def get_Pf(self):
        Pf = (self.pulse_power*self.KND_antenna*BF_grass_times*3e8*self.pulse_duration*self.illuminated_section)/(8*np.pi*(self.observation_range**2))

        return Pf
    
    def get_PG(self, Kp, size_x_ChKP, size_y_ChKP):
        
        PG = (Kp*self.get_Pf()*4*np.pi*(self.observation_range**2)*2*size_x_ChKP*size_y_ChKP)/(self.effective_area_antenna*3e8*self.pulse_duration*self.illuminated_section)

        return PG 


# combo_box.setEditable(True)  # Включаем режим редактирования

"""