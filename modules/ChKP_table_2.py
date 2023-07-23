from PyQt5.QtWidgets import QGraphicsView, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QSlider
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QIcon
from modules.massager import MSGLabel
from PyQt5.QtWidgets import QGraphicsView
import resources


class ChkpTable_2(QWidget):
    def __init__(self, parent_widget):

        super(ChkpTable_2, self).__init__(parent_widget)
        self.parent_widget = parent_widget

        # инициализация ссылки на вивер
        self.image_viewer: QGraphicsView = self.parent_widget.image_view
        # инициализация ссылки на мессенджер
        self.msg: MSGLabel = self.parent_widget.msg

        self.add_SAP = QPushButton('', self)
        self.add_SAP.setFixedSize(155,30)
        pixmap = QPixmap(':/btn/qt_forms/resources/add_RCA.png')
        self.add_SAP.setIcon(QIcon(pixmap))
        self.add_SAP.setText('Добавить элемент САП')

        self.del_SAP = QPushButton('', self)
        self.del_SAP.move(165,0)
        self.del_SAP.setFixedSize(155,30)
        pixmap = QPixmap(':/btn/qt_forms/resources/del_RCA.png')
        self.del_SAP.setIcon(QIcon(pixmap))
        self.del_SAP.setText('Удалить элемент САП')

        self.get_RLI_with_SAP = QPushButton('', self)
        self.get_RLI_with_SAP.move(330,0)
        self.get_RLI_with_SAP.setFixedSize(161,30)
        pixmap = QPixmap(':/btn/qt_forms/resources/save_RCA.png')
        self.get_RLI_with_SAP.setIcon(QIcon(pixmap))
        self.get_RLI_with_SAP.setText('Сформировать РЛИ с САП')

        self.table = QTableWidget(self)
        self.table.move(0,40)
        self.table.setFixedSize(496, 170)
        # Создание заголовков таблицы
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Положение X\n(пиксель)", "Положение Y\n(пиксель)", "Интенсивность\n(помеха/фон)", "Размер X\n(метр)", "Размер Y\n(метр)"])
        # Выравнивание ширины столбцов
        total_width = self.table.width()-17
        column_count = self.table.columnCount()
        column_width = total_width / column_count

        for col in range(column_count):
            self.table.setColumnWidth(col, int(column_width))

        # Виджеты для выбора типа интенсивностей
        title = QLabel("Интенсивность:", self)
        title.move(3,225)
        self.var1 = QLabel("<html><b>помеха/фон</b></html>", self)
        self.var1.move(90,225)
        self.slider = QSlider(Qt.Horizontal, self) # type: ignore
        self.slider.move(180, 225)
        self.slider.setFixedSize(30,20)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1)
        self.slider.setValue(0)
        self.slider.setTickInterval(1)  # Отображаем риски только для значений 0 и 1
        self.var2 = QLabel("метр квадратный", self)
        self.var2.move(220,225)

        # создаем хранилище индексов ЧКП
        self.Chkp_index_list = []

        # Привязка события
        self.add_SAP.clicked.connect(self.add_element)
        self.del_SAP.clicked.connect(self.del_element)
        self.get_RLI_with_SAP.clicked.connect(self.get_ChKP_param_to_solve_SAP)
        self.table.cellChanged.connect(self.handle_cell_changed)

        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.valueChanged.connect(self.change_value)

    def set_init(self):
        """Метод восстанавливает начальное состояние виджета"""
        if hasattr(self, 'Chkp_index_list'):
            if self.Chkp_index_list:
                # Очистка левого окна от меток
                for label in self.Chkp_index_list:
                    self.image_viewer.graphics_scene.removeItem(label)
        self.Chkp_index_list = []
        # Если строки таблицы заполнялись
        if self.table.rowCount():
            self.table.clearContents()
            self.table.setRowCount(0)

    def change_value(self, value) -> None:
        if value:
            self.table.horizontalHeaderItem(2).setText("Интенсивность\n(метр)")
            self.var2.setText("<html><b>метр квадратный</b></html>")
            self.var1.setText("помеха/фон")
            return
        self.table.horizontalHeaderItem(2).setText("Интенсивность\n(помеха/фон)")
        self.var1.setText("<html><b>помеха/фон</b></html>")
        self.var2.setText("метр квадратный")
        



    def slider_pressed(self):
        if self.slider.value() == 0:
            self.slider.setValue(1)
            return
        self.slider.setValue(0)
        
 
    def add_element(self) -> None:
        # визуальное отражение
        if 0 in self.Chkp_index_list:
            self.msg.set_text('Не установлена метка для ЧКП', color = "r")
            return
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)
        self.Chkp_index_list.append(0)

    def del_element(self) -> None:
        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            self.table.removeRow(row)
            label = self.Chkp_index_list.pop(row)
            if label:
                self.image_viewer.graphics_scene.removeItem(label)

    def get_ChKP_param_to_solve_SAP(self) -> None:
        """Метод передает параметры ЧКП в родительский метод и вызывает процесс реформирования свертки с РОИ."""
        # Сбор параметров ЧКП из таблицы
        ChKP_param = self.data_collector()
        if not ChKP_param:
            self.msg.set_text("Не введены данные ЧКП", color="r")
            return
        self.parent_widget.solving_SAP(ChKP_param)

    def update_coord_ChKP(self, number_row: int, value: QPointF) -> None:
        # обновление ячеек координат при изменении меток
        x_pos = QTableWidgetItem(str(round(value.x())))
        y_pos = QTableWidgetItem(str(round(value.y())))
        self.table.setItem(number_row, 0 , x_pos)
        self.table.setItem(number_row, 1 , y_pos)

    def handle_cell_changed(self, row, column):
        # Получение значения из ячейки
        item = self.table.item(row, column)
        if item is not None:
            try:
                label = self.Chkp_index_list[row]
                if not label:
                    self.msg.set_text("Установите метку ЧКП")
                    self.table.blockSignals(True)
                    self.table.setItem(row, column, QTableWidgetItem(''))  # Очистить ячейку
                    self.table.blockSignals(False)
                    return
                if column == 4:
                    float(item.text())
                    return
                val = int(item.text())
                # если изменяются первая и вторая колонка
                if column == 0 or column == 1:
                    current_pos = label.pos()  # Текущая позиция метки
                    new_pos = current_pos  # Создаем копию текущей позиции метки
                    if column == 0: 
                        # Получение текущего размера метки
                        size_x = label.boundingRect().width()
                        new_pos.setX(val-size_x/2)  # Изменяем только координату X
                    else:
                        # Получение текущего размера метки
                        size_y = label.boundingRect().height()
                        new_pos.setY(val-size_y/2)  # Изменяем только координату Y
                    label.setPos(new_pos) # устанавливаем новую позицию

            except ValueError:
                # В ячейке введен некорректный формат данных
                self.table.blockSignals(True)  # Блокировка сигналов, чтобы избежать рекурсии
                self.setItem(row, column, QTableWidgetItem(''))  # Установка пустого значения
                self.table.blockSignals(False)  # Разблокировка сигналов
                self.msg.set_text(f'Введен некорректный формат данных', color = 'r')
                
    def data_collector(self):
        data_ChKps = []
        if self.table.rowCount() != -1:
            for row in range(self.table.rowCount()):
                data_ChKp = []
                # тут путаница со столбцами
                for column in range(self.table.columnCount()):
                    item = self.table.item(row, column)
                    if item is None or not item.text():
                        self.msg.set_text(f'Введены не все данные для ЧКП №{row+1}')
                        return False
                    # тут производится пересчет положения ЧКП из пикселей в отсчеты
                    if column == 0:
                        value = round(int(item.text())*self.image_viewer.coef_px_to_count[0])
                    elif column == 1:
                        value = round(int(item.text())*self.image_viewer.coef_px_to_count[1])
                    elif column == 2:

                        if not self.slider.value():
                            chkp_fon = self.parent_widget.RSA_param.get("Коэффициент сигнал/фон", 0)
                            value = float(item.text())*chkp_fon/(40000/(int(self.table.item(row, 3).text())*int(self.table.item(row, 4).text())))
                        else:
                            fon_DB = self.parent_widget.RSA_param.get("Значение фона в дБ", 0)
                            Kp = float(item.text())/(10**(fon_DB/10))
                            value = Kp/(40000/(int(self.table.item(row, 3).text())*int(self.table.item(row,4).text())))
                    else:
                        value = int(item.text())
                    data_ChKp.append(value)
                data_ChKps.append(data_ChKp)

        return data_ChKps
    

    



        