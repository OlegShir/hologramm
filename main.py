import sys
import os.path
from PyQt5 import QtWidgets, uic
from modules.image_viewer import ImageView
from modules.ChKP_table import ChkpTable
from modules.base_RSA import Adapter
import modules.file_manager as fm
from modules.massager import MSGLabel
from modules.convolution2 import Convolution
from modules.image_analizator import ImageAnalizator



class add_RCA(QtWidgets.QDialog):
    """Класс окна для изменения/добавления РСА"""

    def __init__(self, list_RSA):
        super(add_RCA, self).__init__()
        # загрузка файла интерфейса окна
        uic.loadUi('qt_forms/add_RCA.ui', self)
        self.list_RSA_win.addItems(list_RSA[1:])

        self.add.clicked.connect(
            self.addition)  # нажатие кнопки 'добавить'
        self.change.clicked.connect(
            self.changing)  # нажатие кнопки 'изменить'
        self.remove.clicked.connect(
            self.removal)  # нажатие кнопки 'удалить'

    def addition(self) -> None:
        pass

    def changing(self) -> None:
        pass

    def removal(self) -> None:
        pass


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
        # если выбрана голограмма
        self.selected_hologram: str = ''

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
        # явно передаем в левый вивер таблицу ЧКП и мессенджер
        self.image_view.set_link(self.table_Chkp, self.msg)
        # явно передаем таблицу ЧПК в левый вивер и мессенджер
        self.table_Chkp.set_link(self.image_view, self.msg)

        # нажатие открыть фаил
        self.open_file.clicked.connect(self.opening_file)
        # нажатие изменение РСА
        self.add_RSA.clicked.connect(self.adding_RSA)
        # нажатие вывести РЛ-изображение
        self.get_RLI.clicked.connect(self.getting_RLI)
        # нажатие вывести создать САП
        self.create_SAP.clicked.connect(self.creating_SAP)
        # нажатие добавить элемент САП
        self.add_element_SAP.clicked.connect(self.creating_element_SAP)
        # нажатие удалить элемент САП
        self.del_element_SAP.clicked.connect(self.delete_element_SAP)
        # нажатие рассчитать элемент САП
        self.solve_SAP.clicked.connect(self.solving_SAP)
        # нажатие провести оценку
        self.bt_get_estimation.clicked.connect(self.get_estimation)
        # нажатие сохранить РЛИ
        self.save_img_RSA.clicked.connect(self.saving_img_RSA)

        # обновление данных о РСА
        self.get_RSA()

        self.change_RSA_KA.addItems(["","RadarSAT"])
        # показ окна программы
        self.show()
    
    def saving_img_RSA(self) -> None:
        self.msg.set_text("РЛИ сохранено ...")

    def saving_SAP(self) -> None:
        self.msg.set_text("РЛИ сохранено ...")

    def opening_file(self) -> None:
        """Метод загрузки файла голограммы (*.rgg) или изображения(*.jpg)."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите голограмму или РЛ-изображение", "", "PCA (*.rgg *.jpg)")
        # если фаил выбран
        if file_path:
            self.file_path_prj, self.file_name, file_type = fm.get_file_parameters(file_path)
            if file_type == 'jpg' or file_type == 'JPG':
                # проверяем существование голограммы и файла параметров РСА
                if not os.path.exists(f'{self.file_path_prj}/{self.file_name}.rgg') \
                   or not os.path.exists(f'{self.file_path_prj}/{self.file_name}.json'):
                    self.msg.set_text(
                        'Отсутствуют файл голограммы или параметров РСА\nОткройте фаил голограммы')
                    return
                self.image_view.open_file(file_path)
                # установка в "выбор типа РСА" тип РСА из файла RSA.json
                type_RSA_img = fm.project_json_reader(f'{self.file_path_prj}/{self.file_name}.json', 'РСА')
                # если РСА есть в списке
                if type_RSA_img in self.list_RSA:
                    # выставляем его в поле
                    self.change_RSA.setCurrentText(type_RSA_img)
                # активация кнопки "создать САП", "сохранение РЛ-изображения"
                self.activate_gui(self.create_SAP, self.save_img_RSA)
            elif file_type == 'rgg':
                self.activate_gui(self.change_RSA, self.add_RSA, self.get_RLI)
            else:
                self.msg.set_text('Данный формат не поддерживается')


    def get_RSA(self) -> None:
        """Функция позволят получить список РСА, которые есть в программе и хранятся в json.
           Данные вставляются в выпадаю список 'Выбор типа авиационного РСА'"""
        # подключение к базе РСА
        self.RSA = Adapter('json', 'RSA.json')
        # получаем все типы РСА
        self.list_RSA = self.RSA.connect.get_list_RSA()
        # обновление данных
        self.change_RSA.addItems(self.list_RSA)

    def adding_RSA(self) -> None:
        """Функция запускает виджет для редактирования РСА в программе"""
        RSA = add_RCA(self.list_RSA)
        RSA.exec_()  # запуск класса

    def getting_RLI(self) -> None:
        """Функция полную свертку голограммы для получения РЛИ + создает фаил проекта"""
        select_RSA = self.change_RSA.currentText()
        if not select_RSA:
            self.msg.set_text('Не выбрана РСА')
            return
        # сохранение параметров РСА
        self.param_RSA = self.RSA.connect.get_list_param_RLS(select_RSA)
        # пошла свертка полной РГГ
        self.msg.set_text("Расчет РЛИ", color= 'y')
        '''
        self.convolution = Convolution(param_RSA, f'{self.file_path_prj}/{self.file_name}.rgg')
        self.convolution.range_convolution_ChKP()
        self.convolution.azimuth_convolution_ChKP()
        '''
        self.activate_gui(self.create_SAP, self.save_img_RSA)


    def creating_SAP(self) -> None:
        # Set the table headers
        self.table_Chkp.activate_table()
        self.activate_gui(self.add_element_SAP)

    def solving_SAP(self) -> None:
        """Получение РЛИ с ЧКП"""
        # сбор параметров ЧКП вида   [[размер ЧКП по наклонной дальности, размер ЧКП по азимуту, мощность ЧПК,
        #                              координата x ЧКП внутри исходной РГГ (отсчеты), координата у ЧКП внутри исходной РГГ (отсчеты)], [...]...]
        ChKP_params = self.table_Chkp.data_collector()
        if ChKP_params is not None:
            ROI = self.image_view.get_visible_pixels()
            RCA_param = [10944+64, 165500, 400e6, 0.0351, 485.692e-6, 300e6, 10e-6, 108, 0.23, 4180]
            try:
                RLI = Convolution(RCA_param, f'{self.file_path_prj}/{self.file_name}.rgg', ChKP_param=ChKP_params, auto_px_norm='hemming')
                RLI.range_convolution_ChKP()
                self.msg.set_text("РГГ свернута по дальности")
                RLI.azimuth_convolution_ChKP(ROI=ROI)
                self.msg.set_text("РГГ свернута по азимуту")
                "решене"
                self.image_analizator.open_file(f'{self.file_path_prj}/{self.file_name}.png')
                self.activate_gui(self.save_SAP)
            except Exception as e:
                print(e)
                self.msg.set_text("Количество отсчетов отличается от РСА", color='r')

    def creating_element_SAP(self) -> None:
        self.activate_gui(self.del_element_SAP, self.save_SAP, self.create_SAP, self.save_param_SAP, self.solve_SAP)
        self.table_Chkp.add_element()

    def delete_element_SAP(self) -> None:
        self.table_Chkp.delete_element()

    def get_estimation(self) -> None:
        self.PGk.setText('18 Вт')
        self.Ksab.setText('1,2')

    def activate_gui(self, *args, status: bool = True) -> None:
        '''Метод включает/выключает поданные элементы Qt'''
        for arg in args:
            arg.setEnabled(status)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainForm()
    app.exec_()
