from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap
from typing import List, Union
from modules.massager import MSGLabel
from PyQt5.QtWidgets import QGraphicsView


class ChkpTable(QTableWidget):
    def __init__(self, parent=None):
        super(ChkpTable, self).__init__(parent)
        self.setGeometry(1, 33, 525, 190)
        # создаем хранилище индексов ЧКП
        self.Chkp_index_list = []
        # Привязка события cellChanged к обработчику
        self.cellChanged.connect(self.handle_cell_changed)
        # инициализация ссылки на вивер
        self.image_viewer: QGraphicsView
        # инициализация ссылки на мессенджер
        self.msg: MSGLabel

    def activate_table(self) -> None:
        # Создание заголовков таблицы
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ["Положение X", "Положение  Y", "Вынос X", "Вынос Y", "Интенсивность", "Размер X", "Размер Y"])
        self.resizeColumnsToContents()

    def add_element(self) -> None:
        # визуальное отражение
        if 0 in self.Chkp_index_list:
            self.msg.set_text('Не установлена метка для ЧКП', color = "r")
            return
        rowPosition = self.rowCount()
        self.insertRow(rowPosition)
        self.Chkp_index_list.append(0)

        # логическое отражение

    def delete_element(self) -> None:
        if self.currentRow() >= 0:
            row = self.currentRow()
            self.removeRow(row)
            label = self.Chkp_index_list.pop(row)
            if label:
                self.image_viewer.graphics_scene.removeItem(label)

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
                label = self.Chkp_index_list[row]
                if not label:
                    self.msg.set_text("Установите метку ЧКП")
                    self.blockSignals(True)
                    self.setItem(row, column, QTableWidgetItem(''))  # Очистить ячейку
                    self.blockSignals(False)
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
                self.blockSignals(True)  # Блокировка сигналов, чтобы избежать рекурсии
                self.setItem(row, column, QTableWidgetItem(''))  # Установка пустого значения
                self.blockSignals(False)  # Разблокировка сигналов
                self.msg.set_text(f'Введен некорректный формат данных', color = 'r')
                
    def data_collector(self):
        if self.rowCount() != -1:
            data_ChKps = []
            for row in range(self.rowCount()):
                data_ChKp = []
                # тут путаница со столбцами
                for column in range(self.columnCount()):
                    item = self.item(row, column)
                    if item is None or not item.text():
                        self.msg.set_text(f'Введены не все данные в стоке {row+1}')
                        return
                    if column == 4:
                        value = float(item.text())
                    else:
                        value = int(item.text())
                    if column == 2:
                        data_ChKp[0] += value
                        continue
                    if column == 3:
                        data_ChKp[1] += value
                        continue
                    data_ChKp.append(value)
                data_ChKps.append(data_ChKp)

            return data_ChKps
    
    def set_link(self, image_viewer, msg):
        self.image_viewer = image_viewer
        self.msg = msg
    
    



        
