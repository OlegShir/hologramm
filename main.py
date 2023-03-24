import sys
import os.path
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPixmap
from modules.base_RSA import Adapter
from modules.SAP import TableSAP


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
        # временное хранение данных о РСА если обработка уже осуществлялась (загрузка изображения)
        self.type_RSA_for_img: str = ''

        # загрузка файла интерфейса основного окна
        uic.loadUi('qt_forms/qt_main_new2.ui', self)
        # нажатие открыть фаил
        self.open_file.clicked.connect(self.get_file)
        # нажатие изменение РСА
        self.add_RSA.clicked.connect(self.added_RSA)
        # нажатие вывести РЛ-изображение
        self.get_img.clicked.connect(self.getting_img)
        # нажатие вывести создать САП
        self.create_SAP.clicked.connect(self.creating_SAP)
        self.add_element_SAP.clicked.connect(self.creating_element_SAP)
        self.del_element_SAP.clicked.connect(self.delete_element_SAP)
        # обновление данных о РСА
        self.get_RSA()
        # показ окна программы
        self.show()

    def get_file(self) -> None:
        """Метод загрузки файла голограммы (*.rgg) или изображения(*.jpg)."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите голограмму или РЛ-изображение", "", "PCA (*.rgg *.jpg)")

        # если фаил выбран -> сохраняем путь gпроекта и имя файла
        if file_path:
            # получаем путь к проекту
            self.file_path_prj = "/".join(file_path.split("/")[0:-1])
            # получаем полное имя файла
            file = file_path.split("/")[-1]
            # определяем расширения файла и его имя
            self.file_name = file[:-4]
            file_type = file[-3:]
            # если выбран фаил jpg
            if file_type == 'jpg' or file_type == 'JPG':
                # проверяем существование голограмыы и файла параметров РСА
                if not os.path.exists(f'{self.file_path_prj}/{self.file_name}.rgg') \
                   or not os.path.exists(f'{self.file_path_prj}/{self.file_name}.json'):
                    print(
                        'Отсутствуют файл голограммы или параметров РСА\nОткройте фаил голограммы')
                    # return
                # вывод изобажения на канвас
                scene = QtWidgets.QGraphicsScene(self)
                pixmap = QPixmap(file_path)
                #!!! тут изменение масштаба изображения
                scene.addItem(QtWidgets.QGraphicsPixmapItem(pixmap.scaled(
                    self.canvas_RSA.width()*2, self.canvas_RSA.height()*2)))
                self.canvas_RSA.setScene(scene)
                # установка в "выбор типа РСА" тип РСА из файла RSA.json
                info_RSA = Adapter(
                    'json', f'{self.file_path_prj}/{self.file_name}.json')
                type_RSA_img = info_RSA.connect.get_info_RSA()
                if type_RSA_img in self.list_RSA:
                    self.type_RSA_for_img = type_RSA_img
                    self.change_RSA.setCurrentText(self.type_RSA_for_img)
                # активация кнопки "создать САП", "сохранение РЛ-изображения"
                self.activate_gui(self.create_SAP, self.save_img_RSA)
            else:
                self.selected_hologram = file_path
                self.activate_gui(self.change_RSA, self.add_RSA, self.get_img)

            # активация кнопки "создать САП"
            self.activate_gui(self.create_SAP)

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
        self.activate_gui(self.solve_SAP, self.save_SAP)

    def creating_element_SAP(self) -> None:
        self.SAP.add_element()

    def delete_element_SAP(self) -> None:
        self.SAP.delete_elevent()

    def activate_gui(self, *args: QtWidgets, status: bool = True) -> None:
        '''Метод включает/выключает поданные элементы Qt'''
        for arg in args:
            arg.setEnabled(status)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainForm()
    app.exec_()
