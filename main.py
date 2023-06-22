import sys
import os.path
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPixmap
from modules.image_viever import ImageView
from modules.base_RSA import Adapter
from modules.SAP import TableSAP
import modules.file_manager as fm


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
        # если выбрана голограмма
        self.selected_hologram: str = ''

        # загрузка файла интерфейса основного окна
        uic.loadUi('qt_forms/qt_main_new2.ui', self)
        # загрузка интерфейса левого окна
        self.image_view = ImageView(self)

        # нажатие открыть фаил
        self.open_file.clicked.connect(self.opening_file)

        # нажатие изменение РСА
        self.add_RSA.clicked.connect(self.added_RSA)

        # нажатие вывести РЛ-изображение
        self.get_img.clicked.connect(self.getting_img)

        # нажатие вывести создать САП
        self.create_SAP.clicked.connect(self.creating_SAP)
        self.add_element_SAP.clicked.connect(self.creating_element_SAP)
        self.del_element_SAP.clicked.connect(self.delete_element_SAP)
        self.solve_SAP.clicked.connect(self.solving_SAP)

        self.bt_get_estimation.clicked.connect(self.get_estimation)

        # обновление данных о РСА
        self.get_RSA()

        self.change_RSA_KA.addItems(["","RadarSAT"])
        # показ окна программы
        self.show()
    
   

    def opening_file(self) -> None:
        """Метод загрузки файла голограммы (*.rgg) или изображения(*.jpg)."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите голограмму или РЛ-изображение", "", "PCA (*.rgg *.jpg)")
        # если фаил выбран
        if file_path:
            file_path_prj, file_name, file_type = fm.get_file_parameters(file_path)
            if file_type == 'jpg' or file_type == 'JPG':
                # проверяем существование голограммы и файла параметров РСА
                if not os.path.exists(f'{file_path_prj}/{file_name}.rgg') \
                   or not os.path.exists(f'{file_path_prj}/{file_name}.json'):
                    print(
                        'Отсутствуют файл голограммы или параметров РСА\nОткройте фаил голограммы')
                    return
                self.image_view.open_file(file_path)
                # установка в "выбор типа РСА" тип РСА из файла RSA.json
                type_RSA_img = fm.project_json_reader(f'{file_path_prj}/{file_name}.json', 'РСА')
                if type_RSA_img in self.list_RSA:
                    self.change_RSA.setCurrentText(type_RSA_img)
                # активация кнопки "создать САП", "сохранение РЛ-изображения"
                self.activate_gui(self.create_SAP, self.save_img_RSA)
            elif file_type == 'rgg':
                self.activate_gui(self.change_RSA, self.add_RSA, self.get_img)
            else:
                pass

            # активация кнопки "создать САП"
            # self.activate_gui(self.create_SAP)



    def get_RSA(self) -> None:
        # подключение к базе РСА
        self.RSA = Adapter('json', 'RSA.json')
        # получаем все типы РСА
        self.list_RSA = self.RSA.connect.get_list_RSA()
        # обновление данных
        self.change_RSA.addItems(self.list_RSA)

    def added_RSA(self) -> None:
        RSA = add_RCA(self.list_RSA)
        RSA.exec_()  # запуск класса

    def getting_img(self) -> None:
        select_RSA = self.change_RSA.currentText()
        if select_RSA:
            param_RSA = self.RSA.connect.get_list_param_RLS(select_RSA)
            print(param_RSA)
            self.activate_gui(self.create_SAP, self.seve_img_RSA)

    def creating_SAP(self) -> None:
        # Set the table headers
        self.SAP = TableSAP(self.table_SAP)
        self.activate_gui(self.add_element_SAP)

    def solving_SAP(self) -> None:
        self.activate_gui(self.save_SAP)

    def creating_element_SAP(self) -> None:
        self.activate_gui(self.del_element_SAP, self.save_SAP, self.create_SAP, self.save_param_SAP, self.solve_SAP)
        self.SAP.add_element()

    def delete_element_SAP(self) -> None:
        self.SAP.delete_elevent()

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
