import sys
import os.path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QSlider, QGridLayout
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon

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

class MainForm(QtWidgets.QMainWindow):
    """Класс основного окна программы"""

    def __init__(self):
        super(MainForm, self).__init__()


        # загрузка файла интерфейса основного окна
        uic.loadUi('qt_forms/qt_main_new2.ui', self)
        pixmap = QPixmap(':/ico/qt_forms/resources/icon.png')
        self.setWindowIcon(QIcon(pixmap))



        # выделенное место для программы свертки
        self.convolution: Convolution

        # Создание виджета мессенджера
        self.msg = MSGLabel(self)

        # Создание виджета "Тип авиационного РСА"
        layout_type_RSA = QtWidgets.QVBoxLayout(self.type_RSA_2)
        self.type_RSA_widget = TypeRSA(parent_widget=self)
        layout_type_RSA.addWidget(self.type_RSA_widget)
        # Создание виджета левого окна

        self.image_view = ImageView(self)
        # Создание виджета правого окна
        self.image_analizator = ImageAnalizator(self)

        # Создание мессенджера
        self.msg = MSGLabel(self)

        # Создание виджета на первой вкладке с параметрами ЧКП
        layout_ChKP = QtWidgets.QVBoxLayout(self.tabWidget.widget(0))
        self.table_Chkp_2 = ChkpTable_2(parent_widget=self) 
        layout_ChKP.addWidget(self.table_Chkp_2) 
        # явно передаем в левый вивер таблицу ЧКП и мессенджер
        self.image_view.set_link(self.table_Chkp_2, self.msg, self.label_meters_x, self.label_meters_y)
        
        # Создание виджетов ползунков
        layout_slt = QtWidgets.QVBoxLayout(self.tabWidget.widget(1))
        self.slider_image_analizator = SliderIMG(parent_widget=self)
        # Добавление ползунков на вторую вкладку
        layout_slt.addWidget(self.slider_image_analizator)

        # Создание виджетов амплитудных характеристик
        layout_ampl = QtWidgets.QVBoxLayout(self.Amp_character)
        self.ampl_char = AmplChar(parent_widget = self)
        # Добавление ползунков на вторую вкладку
        layout_ampl.addWidget(self.ampl_char)

        # Создание виджетов для перерасчета параметров для КА
        layout_RSA_KA = QtWidgets.QVBoxLayout(self.RSA_KA_box)
        self.RSA_KA = RSAKABOX(parent_widget = self)
        # Добавление ползунков на вторую вкладку
        layout_RSA_KA.addWidget(self.RSA_KA)

        # Создание виджетов параметров фона
        self.fon_param = FonParam(self)


        # нажатие открыть фаил
        self.open_file.clicked.connect(self.opening_file)
        # нажатие вывести РЛ-изображение
        self.get_RLI.clicked.connect(self.getting_RLI)
        # нажатие сохранить РЛИ
        self.save_full_RLI.clicked.connect(self.saving_img_RSA)

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
                self.activate_gui(self.save_full_RLI,self.tabWidget.widget(0))
                # для правильного расчета метки масштаба в image_view необходимо передать значения коэффициентов пикселей в отсчеты и пикселей в метры, получаемые из dx, ndr и коэффициента сжатия изображение, получаемых из параметров РСА
                coef_px_to_count, coef_px_to_meters = self.scale_factor_px_to_count_and_meters(self.RSA_param)
                self.image_view.set_scale_factor_px_to_count_and_meters(coef_px_to_count, coef_px_to_meters)
                # передаем коэффициент перевода из пикселей в метры в класс ImageAnalizator для расчета линейки
                self.image_analizator.set_coef_px_to_meters(coef_px_to_meters)
                self.image_view.open_file(file_path)
                self.fon_param.set_init_OK_param(self.RSA_param.get("Значение фона в дБ"))
            elif file_type == 'rgg':
                self.type_RSA_widget.btn_param.setEnabled(True)
            else:
                self.msg.set_text('Данный формат не поддерживается')

    def getting_RLI(self) -> None:
        """Функция полную свертку голограммы для получения РЛИ + создает фаил проекта"""
        # пошла свертка полной РГГ
        self.msg.set_text("Расчет РЛИ", color= 'y')
        self.convolution = Convolution(self.RSA_param, f'{self.file_path_prj}', f'{self.file_name}', self.RSA_name)
        self.convolution.range_convolution_ChKP()
        self.convolution.azimuth_convolution_ChKP()
        # Создание JSON файл проекта
        self.file_worker.project_json_writer(self.RSA_name, self.RSA_param)
        self.image_view.open_file(f'{self.file_path_prj}/{self.file_name}.png')
        self.activate_gui(self.save_full_RLI)
        self.fon_param.set_init_NOT_param()

    def solving_SAP(self, ChKP_params) -> None:
        """Получение РЛИ с ЧКП"""
        # сбор параметров ЧКП вида   [[размер ЧКП по наклонной дальности, размер ЧКП по азимуту, мощность ЧПК,
        #                              координата x ЧКП внутри исходной РГГ (отсчеты), координата у ЧКП внутри исходной РГГ (отсчеты)], [...]...]
        # Получаем список ROI в отсчетах
        ROI = self.image_view.get_ROI_RLI_in_count()
        try:
            RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ChKP_params, ROI=ROI, save_ROI_to_np=True)
            RLI.range_convolution_ChKP()
            RLI.azimuth_convolution_ChKP()
            self.image_analizator.open_file(f'{self.file_path_prj}/{self.file_name}_ROI.png')
            self.activate_gui(self.tabWidget.widget(1), self.tabWidget.widget(2))
        except Exception as e:
            print(e)
            self.msg.set_text("Количество отсчетов отличается от РСА", color='r')
        self.activate_gui(self.tabWidget.widget(1), self.tabWidget.widget(2))

    def solving_fon(self, ROI):
        # Вычисление среднего значения фона
        RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ROI=ROI, fon=True)
        RLI.range_convolution_ChKP()
        ave_fon = RLI.azimuth_convolution_ChKP()
        # Вычисление среднего значения ЧКП
        RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ROI=ROI, fon=True, ChKP_param=[[ROI[0]+ROI[2]//2,
                                                                                                                             ROI[1]+ROI[3]//2, 
                                                                                                                             100, 
                                                                                                                             1000, 
                                                                                                                             1000]])
        RLI.range_convolution_ChKP()
        ave_ChKP = RLI.azimuth_convolution_ChKP()
        # Коэффициент сигнал/фон
        coef_signal_fon = (100*ave_fon)/ave_ChKP # type: ignore
        # Записываем значение в словарь и фаил JSON
        self.RSA_param["Коэффициент сигнал/фон"] = coef_signal_fon
        self.RSA_param["Значение фона в дБ"] = float(self.fon_param.fon_DB.text())
        # Записываем значения в JSON
        self.file_worker.update_json_value(["Коэффициент сигнал/фон","Значение фона в дБ"],
                                            [self.RSA_param["Коэффициент сигнал/фон"],
                                             self.RSA_param["Значение фона в дБ"] 
                                            ]
                                          )
        self.fon_param.set_init_OK_param(self.RSA_param["Значение фона в дБ"])
        self.activate_gui(self.tabWidget.widget(0))

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
                          self.tabWidget.widget(0),
                          self.tabWidget.widget(1),
                          self.tabWidget.widget(2),
                          status=False)
        self.fon_param.set_init()
        self.table_Chkp_2.set_init()
        self.slider_image_analizator.set_init()
        self.RSA_KA.set_init()
        self.ampl_char.set_init()
        
        

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

        return [coef_px_to_count_x, coef_px_to_count_y], [coef_px_to_meters_x, coef_px_to_meters_y]
    
    def saving_img_RSA(self) -> None:
        self.image_view.save_image()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainForm()
    app.exec_()
