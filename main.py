import sys, csv
import os.path, os
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QFrame, QTabWidget, QPushButton
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon, QFont

from modules.image_viewer import ImageView
from modules.ChKP_table_2 import ChkpTable_2
from modules.file_manager import FileWorker
from modules.massager import MSGLabel
from modules.convolution6 import Convolution
from modules.image_analizator import ImageAnalizator
from modules.sliders_img import SliderIMG
from modules.ampl_char import AmplChar
from modules.type_RSA_widget import TypeRSA
from modules.constant import RSA
from modules.fon_param import FonParam
from modules.RSA_KA_box import RSAKABOX

from modules.helper import help

os.system('mode con: cols=100 lines=10')

class MainForm(QtWidgets.QMainWindow):
    """Класс основного окна программы"""

    def __init__(self):
        super(MainForm, self).__init__()

        # параметры основного окна
        self.setWindowTitle("Модель САП")
        self.setFixedSize(1100, 650)
        pixmap = QPixmap(':/ico/qt_forms/resources/icon.png')
        self.setWindowIcon(QIcon(pixmap))

        # выделенное место для программы свертки
        self.convolution: Convolution
        
        #----------------Создание виджетов----------------#
        font_bolt = QFont()
        font_bolt.setBold(True)
        # виджет левого окна
        self.label_left = QLabel("Исходное РЛИ", self)
        self.label_left.setFont(font_bolt)
        self.label_left.setGeometry(200, 0, 171, 30)
        self.image_view = ImageView(self)
        # разметка масштаба для левого окна
        self.label_meters_x = QLabel(self)
        self.label_meters_x.setFont(font_bolt)
        self.label_meters_x.setGeometry(245, 390, 50, 13)
        self.label_meters_y = QLabel(self)
        self.label_meters_y.setFont(font_bolt)
        self.label_meters_y.setGeometry(530, 205, 50, 13)
        # линии
        geometric_line = [QRect(300, 390, 221, 16), QRect(5, 390, 220, 16),QRect(525, 372, 9, 16), QRect(525, 23, 9, 16),
                          QRect(520, 385, 3, 12), QRect(533, 30, 3, 170), QRect(5, 385, 3, 12), QRect(5, 385, 3, 12),  QRect(533, 220, 3, 160)]
        for i in range(len(geometric_line)):
            line = QFrame(self)
            line.setGeometry(geometric_line[i])
            if i < 4:
                line.setFrameShape(QFrame.HLine)
            else: line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Sunken)

        # виджет правого окна
        self.label_right = QLabel("<html><b>РЛИ с САП</html></b>", self)
        self.label_right.setGeometry(800, 0, 171, 30)
        self.image_analizator = ImageAnalizator(self)

        # виджет мессенджера сообщения
        self.msg = MSGLabel(self)

        # кнопка "Открыть фаил"
        self.open_file = QPushButton("Открыть фаил", self)
        self.open_file.setGeometry(20, 403, 170, 30)
        self.open_file.setToolTip(help.get('open_file', ""))
        # нажатие "Открыть фаил"
        self.open_file.clicked.connect(self.opening_file)

        # бокс "Тип авиационного РСА"
        self.type_RSA_widget = TypeRSA(parent_widget=self)
        self.type_RSA_widget.setFixedSize(180, 120)
        self.type_RSA_widget.move(20, 440)

        # кнопка "Вывести РЛИ"   
        self.get_RLI = QPushButton("Вывести РЛИ", self)
        self.get_RLI.setGeometry(20, 556, 170, 30)
        # нажатие "Вывести РЛИ"
        self.get_RLI.clicked.connect(self.getting_RLI)

        # кнопка "Сохранить РЛИ"   
        self.save_full_RLI = QPushButton("Сохранить РЛИ", self)
        self.save_full_RLI.setGeometry(20, 593, 170, 30)
        # нажатие "Сохранить РЛИ "
        self.save_full_RLI.clicked.connect(self.saving_img_RSA)

        # таблица с вкладками
        self.tabWidget2 = QTabWidget(self)
        self.tabWidget2.setGeometry(580, 390, 516, 255)

        # создание виджета на первой вкладке с параметрами ЧКП
        self.table_Chkp_2 = ChkpTable_2(parent_widget=self) 
        self.tabWidget2.addTab(self.table_Chkp_2, "Создание САП")

        # создание виджета на второй вкладке с регулировкой изображения
        self.slider_image_analizator = SliderIMG(parent_widget=self)
        self.tabWidget2.addTab(self.slider_image_analizator, "Обработка изображения")

        # создание виджета на третьей вкладке с анализом изображения
        three_tab = QWidget()
        layout = QHBoxLayout()
        three_tab.setLayout(layout)
        self.tabWidget2.addTab(three_tab, "Обработка изображения")
        self.RSA_KA = RSAKABOX(parent_widget = self)
        self.ampl_char = AmplChar(parent_widget = self)
        layout.setSpacing(6)
        layout.addWidget(self.RSA_KA)
        layout.addWidget(self.ampl_char)

        # Создание виджетов параметров фона
        self.fon_param = FonParam(self)

        self.image_view.set_link(self.table_Chkp_2, self.msg, self.label_meters_x, self.label_meters_y)
        self.set_init()
        # показ окна программы
        self.show()
  
    def opening_file(self) -> None:
        """Метод загрузки файла голограммы (*.rgg) или изображения(*.jpg)."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите голограмму или РЛ-изображение", "", "PCA (*.rgg *.jpg *.png)")
        # если фаил выбран
        if file_path:
            self.set_init()
            #  Инициализация класса работы с файлами
            self.file_worker = FileWorker(file_path)
            # Получение данных о файле
            self.file_path_prj, self.file_name, file_type = self.file_worker.get_info_file()
            if file_type == 'jpg' or file_type == 'png':
                # проверяем существование голограммы и файла параметров РСА
                if not os.path.exists(f'{self.file_path_prj}/{self.file_name}.rgg') \
                   or not os.path.exists(f'{self.file_path_prj}/{self.file_name}.json'):
                    self.msg.set_text(
                        'Отсутствуют файл голограммы или параметров РСА\nОткройте фаил голограммы', color= 'r')
                    return
                # считываем json фаил проекта и получем название РСА и его параметры
                try:
                    self.RSA_name, self.RSA_param =self.file_worker.project_json_reader()
                except:
                    self.msg.set_text(
                        'Ошибка в файле описания проекта', color= 'r')
                    return
                # если РСА нет в списке
                if not self.RSA_name in RSA:
                    self.msg.set_text("Изображение сформировано РСА, не входящим в программу")
                    return
                # выставляем его в поле "Тип авиационного РСА"
                self.type_RSA_widget.name_type_RSA.setText(self.RSA_name)
                # активация кнопки "сохранение РЛ-изображения"
                self.activate_gui(self.save_full_RLI,self.tabWidget2.widget(0))
                # для правильного расчета метки масштаба в image_view необходимо передать значения коэффициентов пикселей в отсчеты и пикселей в метры, получаемые из dx, ndr и коэффициента сжатия изображение, получаемых из параметров РСА
                coef_px_to_count, coef_px_to_meters = self.scale_factor_px_to_count_and_meters(self.RSA_param)
                self.image_view.set_scale_factor_px_to_count_and_meters(coef_px_to_count, coef_px_to_meters)
                # передаем коэффициент перевода из пикселей в метры в класс ImageAnalizator для расчета линейки
                self.image_analizator.set_coef_px_to_meters(coef_px_to_meters, coef_px_to_count)
                self.image_view.open_file(file_path)
                self.fon_param.set_init_OK_param(self.RSA_param.get("Значение фона в дБ"))
            elif file_type == 'rgg':
                self.type_RSA_widget.btn_param.setEnabled(True)
            else:
                self.msg.set_text('Данный формат не поддерживается')

    def getting_RLI(self) -> None:
        """Функция полную свертку голограммы для получения РЛИ + создает фаил проекта"""
        # пошла свертка полной РГГ
        os.system("cls")
        self.msg.set_text("Расчет РЛИ", color= 'y')
        self.convolution = Convolution(self.RSA_param, f'{self.file_path_prj}', f'{self.file_name}', self.RSA_name)
        self.convolution.range_convolution_ChKP()
        self.convolution.azimuth_convolution_ChKP()
        # Создание JSON файл проекта
        self.file_worker.project_json_writer(self.RSA_name, self.RSA_param)
        # для правильного расчета метки масштаба в image_view необходимо передать значения коэффициентов пикселей в отсчеты и пикселей в метры, получаемые из dx, ndr и коэффициента сжатия изображение, получаемых из параметров РСА
        coef_px_to_count, coef_px_to_meters = self.scale_factor_px_to_count_and_meters(self.RSA_param)
        self.image_view.set_scale_factor_px_to_count_and_meters(coef_px_to_count, coef_px_to_meters)
        # передаем коэффициент перевода из пикселей в метры в класс ImageAnalizator для расчета линейки
        self.image_analizator.set_coef_px_to_meters(coef_px_to_meters, coef_px_to_count)
        self.image_view.open_file(f'{self.file_path_prj}/{self.file_name}.png')
        self.activate_gui(self.save_full_RLI)
        self.fon_param.set_init_NOT_param()

    def solving_SAP(self, ChKP_params) -> None:
        """Получение РЛИ с ЧКП"""
        # сбор параметров ЧКП вида   [[размер ЧКП по наклонной дальности, размер ЧКП по азимуту, мощность ЧПК,
        #                              координата x ЧКП внутри исходной РГГ (отсчеты), координата у ЧКП внутри исходной РГГ (отсчеты)], [...]...]
        # Получаем список ROI в отсчетах
        os.system("cls")
        ROI = self.image_view.get_ROI_RLI_in_count()
        try:
            RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ChKP_params, ROI=ROI, save_ROI_to_np=True)
            RLI.range_convolution_ChKP()
            RLI.azimuth_convolution_ChKP()
            self.image_analizator.open_file(f'{self.file_path_prj}/{self.file_name}_ROI.png')
            self.activate_gui(self.tabWidget2.widget(1), self.tabWidget2.widget(2))
        except Exception as e:
            print(e)
            self.msg.set_text("Количество отсчетов отличается от РСА", color='r')
        self.activate_gui(self.tabWidget2.widget(1), self.tabWidget2.widget(2))

    def solving_fon(self, ROI):
        os.system("cls")
        # Вычисление среднего значения фона
        RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ROI=ROI, fon=True)
        RLI.range_convolution_ChKP()
        ave_fon = RLI.azimuth_convolution_ChKP()
        self.RSA_param["Абсолютное среднее значение фона"] = ave_fon
        # Вычисление среднего значения ЧКП
        size_ChKP = self.image_view.fon_rect_size*self.coef_px_to_meters
        real_power = 50
        RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ROI=ROI, fon=True, ChKP_param=[[ROI[0]-ROI[2],
                                                                                                                             ROI[1]+ROI[3]//2, 
                                                                                                                             real_power, 
                                                                                                                             size_ChKP, 
                                                                                                                             size_ChKP]]) 
        RLI.range_convolution_ChKP()
        ave_ChKP = RLI.azimuth_convolution_ChKP() 
        
                                                                                              
        Chkp = []
        i_count = []
        for i in range(0,50,1):
            RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ROI=ROI, count_fon=str(i), fon=True, ChKP_param=[[ROI[0]-ROI[2],
                                                                                                                                                ROI[1]+ROI[3]//2, 
                                                                                                                                                i, 
                                                                                                                                                size_ChKP, 
                                                                                                                                                size_ChKP]])
        
            RLI.range_convolution_ChKP()
            ave_ChKP = RLI.azimuth_convolution_ChKP()
            Chkp.append(ave_ChKP)
            i_count.append(i)
        Chkp_fon = [x/ave_fon for x in Chkp]   
        # Открываем файл для записи в режиме текста
        with open('output.csv', 'w', newline='') as csvfile:
            # Создаем объект writer для записи в файл
            writer = csv.writer(csvfile)
    
            # Записываем заголовок
            writer.writerow(['List1', 'List2'])

            # Записываем данные из двух списков в разные столбцы
            for item1, item2 in zip(i_count, Chkp_fon):
                writer.writerow([item1, item2])
        print(Chkp_fon)

        # отношение сигнал/фон
        signal_fon = ave_ChKP/ave_fon # type: ignore
        # коэффициент перерасчета real_power = signal_fon/coef_signal_fon

        coef_signal_fon = round(signal_fon/real_power, 2)
        # Записываем значение в словарь и фаил JSON
        self.RSA_param["Коэффициент сигнал/фон"] = coef_signal_fon
        self.RSA_param["Значение фона в дБ"] = float(self.fon_param.fon_DB.text())
        # Записываем значения в JSON
        self.file_worker.update_json_value(["Коэффициент сигнал/фон",
                                            "Значение фона в дБ", 
                                            "Абсолютное среднее значение фона"
                                            ],
                                            [self.RSA_param["Коэффициент сигнал/фон"],
                                             self.RSA_param["Значение фона в дБ"],
                                             self.RSA_param["Абсолютное среднее значение фона"] 
                                            ]
                                          )
        self.fon_param.set_init_OK_param(self.RSA_param["Значение фона в дБ"])
        self.activate_gui(self.tabWidget2.widget(0))

    def set_init(self):
        """Метод возвращает значения программы в исходный вид"""
        # Очистка параметров
        # расположение проекта
        self.file_path_prj: str = ''
        # имя файлов проекта: изображение, голограмма, фаил описания РСА
        self.file_name: str = '' 
        # Наименование РСА
        self.RSA_name = ' '
        # Параметры РСА
        self.RSA_param: dict
        # Изменение параметров виджетов
        self.type_RSA_widget.set_init()
        self.image_view.set_init()
        self.image_analizator.set_init()
        # заголовок масштаба по оси х
        self.label_meters_x.setHidden(True)
        # заголовок масштаба по оси у
        self.label_meters_y.setHidden(True)
        self.activate_gui(self.get_RLI,
                          self.save_full_RLI, 
                          self.tabWidget2.widget(0),
                          self.tabWidget2.widget(1),
                          self.tabWidget2.widget(2),
                          status=False)
        self.tabWidget2.setCurrentIndex(0)
        self.fon_param.set_init()
        self.table_Chkp_2.set_init()
        self.slider_image_analizator.set_init()
        self.RSA_KA.set_init()
        self.ampl_char.set_init()
        os.system("cls")
        

    def activate_gui(self, *args, status: bool = True) -> None:
        '''Метод включает/выключает поданные элементы Qt'''
        for arg in args:
            arg.setEnabled(status)


    def scale_factor_px_to_count_and_meters(self, param_RSA: dict):

        fcvant = param_RSA.get("Частота дискретизации АЦП", 0) 
        Tpi = param_RSA.get("Период повторения импульсов", 0)
        movement_speed = param_RSA.get("Скорость движения носителя", 0)
        coef_resize = param_RSA.get("Коэффициент сжатия", 0)
        
        dnr:float = 3e8 / (2 * fcvant) # шаг по дальности
        dx:float = movement_speed  * Tpi # Шаг по азимуту

        coef_px_to_count_x = 1/(0.25/dnr*coef_resize)
        coef_px_to_count_y = 1/(0.25/dx*coef_resize)
        coef_px_to_meters_x = coef_px_to_count_x * dx
        coef_px_to_meters_y = coef_px_to_count_y * dnr

        self.coef_px_to_meters = coef_px_to_meters_x


        return [coef_px_to_count_x, coef_px_to_count_y], [coef_px_to_meters_x, coef_px_to_meters_y]
    
    def saving_img_RSA(self) -> None:
        self.image_view.save_image()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainForm()
    app.exec_()
