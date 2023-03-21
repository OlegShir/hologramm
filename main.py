import sys, os.path 
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from modules.base_RSA import Adapter


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
        # нажатие открыть голограмму
        self.open_file.clicked.connect(self.get_file)
        self.add_RSA.clicked.connect(?)
        # обновление данных о РСА
        self.get_RCA()
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
                        'отсутствуют файл голограммы или параметров РСА\nОткройте фаил голограммы')
                    return
                # вывод изобажения на канвас
                scene = QtWidgets.QGraphicsScene(self)
                pixmap = QPixmap(file_path)
                #!!! тут изменение масштаба изображения
                scene.addItem(QtWidgets.QGraphicsPixmapItem(pixmap.scaled(self.canvas_RSA.width()*2, self.canvas_RSA.height()*2)))
                self.canvas_RSA.setScene(scene)
            else:
                self.selected_hologram = file_path
                
                self.activate_gui(self.change_RSA, self.add_RSA)

    def get_RCA(self)->None:
        # подключение к базе РСА 
        self.RSA = Adapter('json', 'RSA.json')
        # получаем все типы РСА
        self.list_RSA = self.RSA.connect.get_list_RSA()
        # обновление данных
        self.change_RSA.addItems(self.list_RSA)         



    def activate_gui(self, *args: QtWidgets, status:bool = True)-> None:
        '''Метод включает/выключает поданные элементы Qt'''
        for arg in args:
            arg.setEnabled(status)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainForm()
    app.exec_()
