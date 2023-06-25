from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap
from typing import List, Union

class ChkpTable(QTableWidget):
    def __init__(self, parent=None):
        super(ChkpTable, self).__init__(parent)
        self.setGeometry(1, 33, 525, 190)
        # создаем хранилище индексов ЧКП
        self.Chkp_index_list = []
        # Привязка события cellChanged к обработчику
        self.cellChanged.connect(self.handle_cell_changed)
        # инициализация ссылки на просмоторщик
        self.image_viewer: QGraphicsView

    def activate_table(self) -> None:
        # Создание заголовков таблицы
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ["Положение X", "Положение  Y", "Вынос X", "Вынос Y", "Интенсивность", "Размер X", "Размер Y"])
        self.resizeColumnsToContents()

    def add_element(self) -> None:
        # визуальное отражение
        if 0 in self.Chkp_index_list:
            print('Не установлена метка для ЧКП')
            return
        rowPosition = self.rowCount()
        self.insertRow(rowPosition)
        self.Chkp_index_list.append(0)
        # print(self.table.rowCount())
        # логическое отражение

    def delete_element(self) -> None:
        if self.currentRow() >= 0:
            row = self.currentRow()
            print(row)
            self.removeRow(row)

    def update_coord_ChKP(self, number_row: int, value: QPointF) -> None:
        # обновление ячеек координат при изменении меток
        x_pos = QTableWidgetItem(str(round(value.x())))
        y_pos = QTableWidgetItem(str(round(value.y())))
        self.setItem(number_row, 0 , x_pos)
        self.setItem(number_row, 1 , y_pos)


    def handle_cell_changed(self, row, column):
        # Получение значения из ячейки
        item = self.item(row, column)
        if item is not None:
            try:
                if column == 4:
                    float(item.text())
                    return
                int(item.text())
            except ValueError:
                # В ячейке введен некорректный формат данных
                self.blockSignals(True)  # Блокировка сигналов, чтобы избежать рекурсии
                self.setItem(row, column, QTableWidgetItem(''))  # Установка пустого значения
                self.blockSignals(False)  # Разблокировка сигналов
                print(f'В ячейке ({row}, {column}) введен некорректный формат данных')
                
    def data_collector(self):
        if self.rowCount() != -1:
            data_ChKps = []
            for row in range(self.rowCount()):
                data_ChKp = []
                for column in range(self.columnCount()):
                    item = self.item(row, column)
                    if not item.text() or item is None:
                        print(f'Введены не все данные в стоке {row+1}')
                        return
                    if column == 4:
                        value = float(item.text())
                    else:
                        value = int(item.text())
                    data_ChKp.append(value)
                data_ChKps.append(data_ChKp)

            print(data_ChKps)
            return data_ChKps
    
    def set_link_image_viewer(self, image_viewer):
        self.image_viewer = image_viewer
    
    



        
