import sys
import os.path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QSlider, QGridLayout
from PyQt5 import QtWidgets, uic
from modules.image_viewer import ImageView
from modules.ChKP_table import ChkpTable
from modules.file_manager import FileWorker
from modules.massager import MSGLabel
from modules.convolution5 import Convolution
from modules.image_analizator import ImageAnalizator
from modules.RSA_KA import RSAKA
from modules.sliders_img import SliderIMG
from modules.ampl_char import AmplChar
from modules.type_RSA_widget import TypeRSA
from modules.constant import RSA


class MainForm(QtWidgets.QMainWindow):
    """Класс основного окна программы"""

    def __init__(self):
        super(MainForm, self).__init__()
        # расположение проекта
        self.file_path_prj: str = ''
        # имя файлов проекта: изображение, голограмма, фаил описания РСА
        self.file_name: str = ''
        # выделенное место для программы свертки
        self.convolution: Convolution
        # Индекс выбранного РСА
        self.RSA_name = " "
        self.RSA_param = []

        # загрузка файла интерфейса основного окна
        uic.loadUi('qt_forms/qt_main_new2.ui', self)
        # загрузка интерфейса таблицы ЧКП
        self.table_Chkp = ChkpTable(self.tabWidget.widget(0))  
        # загрузка интерфейса левого окна
        self.image_view = ImageView(self)
        # загрузка интерфейса правого окна
        self.image_analizator = ImageAnalizator(self)
        # загрузка мессенджер
        self.msg = MSGLabel(self)
        # заголовок масштаба по оси х
        self.label_meters_x.setHidden(True)
        # заголовок масштаба по оси у
        self.label_meters_y.setHidden(True)
        # явно передаем в левый вивер таблицу ЧКП и мессенджер
        self.image_view.set_link(self.table_Chkp, self.msg, self.label_meters_x, self.label_meters_y)
        # явно передаем таблицу ЧПК в левый вивер и мессенджер
        self.table_Chkp.set_link(self.image_view, self.msg)

        # self.image_analizator.set_coef_px_to_meters([0.26,0.26])
        # self.image_analizator.open_file('example/example_ROI.png')
        
        # Создание виджетов ползунков
        layout_slt = QtWidgets.QVBoxLayout(self.tabWidget.widget(1))
        self.slider_image_analizator = SliderIMG()
        self.slider_image_analizator.set_link(self.image_analizator)
        # Добавление ползунков на вторую вкладку
        layout_slt.addWidget(self.slider_image_analizator)

        # Создание виджетов амплитудных характеристик
        layout_ampl = QtWidgets.QVBoxLayout(self.Amp_character)
        self.ampl_char = AmplChar()
        # Добавление ползунков на вторую вкладку
        layout_ampl.addWidget(self.ampl_char)
        self.ampl_char.set_link(self.image_analizator)

        # Создание виджетов Тип авиационного РСА
        layout_type_RSA = QtWidgets.QVBoxLayout(self.type_RSA_2)
        self.type_RSA_widget = TypeRSA(parent_widget=self)
        layout_type_RSA.addWidget(self.type_RSA_widget)

        # нажатие открыть фаил
        self.open_file.clicked.connect(self.opening_file)

        # нажатие вывести РЛ-изображение
        self.save_full_RLI.clicked.connect(self.getting_RLI)
        # нажатие вывести создать САП
        self.create_SAP.clicked.connect(self.creating_SAP)
        # нажатие добавить элемент САП
        self.add_element_SAP.clicked.connect(self.creating_element_SAP)
        # нажатие удалить элемент САП
        self.del_element_SAP.clicked.connect(self.delete_element_SAP)
        # нажатие рассчитать элемент САП
        self.solve_SAP.clicked.connect(self.solving_SAP)
        # нажатие провести оценку
        self.bt_get_estimation.clicked.connect(self.getting_estimation)
        # нажатие сохранить РЛИ
        self.save_full_RLI.clicked.connect(self.saving_img_RSA)

        # обновление данных о космических РСА
        # self.get_RSA_KA()

        # показ окна программы
        self.show()
    
    
    def opening_file(self) -> None:
        """Метод загрузки файла голограммы (*.rgg) или изображения(*.jpg)."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите голограмму или РЛ-изображение", "", "PCA (*.rgg *.jpg *.png)")
        # если фаил выбран
        if file_path:
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
                # активация кнопки "создать САП", "сохранение РЛ-изображения"
                self.activate_gui(self.create_SAP, self.save_full_RLI)
                # для правильного расчета метки масштаба в image_view необходимо передать значения коэффициентов пикселей в отсчеты и пикселей в метры, получаемые из dx, ndr и коэффициента сжатия изображение, получаемых из параметров РСА
                coef_px_to_count, coef_px_to_meters = self.scale_factor_px_to_count_and_meters(self.RSA_param)
                self.image_view.set_scale_factor_px_to_count_and_meters(coef_px_to_count, coef_px_to_meters)
                # передаем коэффициент перевода из пикселей в метры в класс ImageAnalizator для расчета линейки
                self.image_analizator.set_coef_px_to_meters(coef_px_to_meters)
                self.image_view.open_file(file_path)
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
        self.activate_gui(self.create_SAP, self.save_full_RLI)

    def creating_SAP(self) -> None:
        # Set the table headers
        self.table_Chkp.activate_table()
        self.activate_gui(self.add_element_SAP)

    def solving_SAP(self) -> None:
        """Получение РЛИ с ЧКП"""
        # сбор параметров ЧКП вида   [[размер ЧКП по наклонной дальности, размер ЧКП по азимуту, мощность ЧПК,
        #                              координата x ЧКП внутри исходной РГГ (отсчеты), координата у ЧКП внутри исходной РГГ (отсчеты)], [...]...]
        # Получаем список ROI в отсчетах
        ROI = self.image_view.get_ROI_in_count()
        # Получение значений ЧКП
        ChKP_params = self.table_Chkp.data_collector()
        if not ChKP_params:
            return           
        
        try:
            RLI = Convolution(self.RSA_param, self.file_path_prj, self.file_name, self.RSA_name, ChKP_params, ROI=ROI)
            RLI.range_convolution_ChKP()
            RLI.azimuth_convolution_ChKP()
            self.image_analizator.open_file(f'{self.file_path_prj}/{self.file_name}_ROI.png')
            self.activate_gui(self.save_SAP)
        except Exception as e:
            print(e)
            self.msg.set_text("Количество отсчетов отличается от РСА", color='r')
     

    def creating_element_SAP(self) -> None:
        self.activate_gui(self.del_element_SAP, self.save_SAP, self.create_SAP, self.save_param_SAP, self.solve_SAP)
        self.table_Chkp.add_element()

    def delete_element_SAP(self) -> None:
        self.table_Chkp.delete_element()

    def getting_estimation(self) -> None:
        """Расчет необходимой мощности РСК КА"""
        # проверяем правильность ввода параметра Кр
        Kp_str = self.Kp_line.text()
        if Kp_str.isdigit():
            Kp = int(Kp_str)
        elif Kp_str.isdecimal():
            Kp = float(Kp_str)
        else:
            self.msg.set_text("Не правильный формат данных", color='r')
            return
        ChKP_params = self.table_Chkp.data_collector()
        if not ChKP_params:
            return
        # получаем параметры выбранного РСА КА
        RSA_KA_param = self.RSA_KA.connect.get_list_param_RSA(self.change_RSA_KA.currentText())
        if RSA_KA_param:
            # создаем экземпляр РСА КА
            RSA_KA = RSAKA(RSA_KA_param) 
            PG = 0
            for i in range(len(ChKP_params)):
                PG += RSA_KA.get_PG(Kp, ChKP_params[i][3], ChKP_params[i][4])
            self.PGk.setText(str(PG))
            

    def activate_gui(self, *args, status: bool = True) -> None:
        '''Метод включает/выключает поданные элементы Qt'''
        for arg in args:
            arg.setEnabled(status)


    def scale_factor_px_to_count_and_meters(self, param_RSA: list):

        _, _, fcvant, _, Tpi, _, _, movement_speed, _, _, coef_resize= param_RSA
        
        dnr:float = 3e8 / (2 * fcvant) # шаг по дальности
        dx:float = movement_speed  * Tpi # Шаг по азимуту

        coef_px_to_count_x = 1/(0.25/dnr*coef_resize)
        coef_px_to_count_y = 1/(0.25/dx*coef_resize)
        coef_px_to_meters_x = coef_px_to_count_x * dx
        coef_px_to_meters_y = coef_px_to_count_y * dnr

        return [coef_px_to_count_x, coef_px_to_count_y], [coef_px_to_meters_x, coef_px_to_meters_y]
    
    def saving_img_RSA(self) -> None:
        self.msg.set_text("РЛИ сохранено ...")

    # def get_RSA_KA(self) -> None:
    #     """Функция позволят получить список РСА КА, которые есть в программе и хранятся в json.
    #        Данные вставляются в выпадаю список 'Выбор типа авиационного РСА'"""
    #     # подключение к базе РСА
    #     self.RSA_KA = Adapter('json', 'RSA_KA.json')
    #     # получаем все типы РСА КА
    #     self.list_RSA_KA = self.RSA_KA.connect.get_list_RSA()
    #     # обновление данных
    #     self.change_RSA_KA.addItems(self.list_RSA_KA)       



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainForm()
    app.exec_()
