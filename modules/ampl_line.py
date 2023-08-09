import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap, QIcon

import resources

class GraphAmplitudeValue:
    def __init__(self, 
                 start_point: QPoint,
                 end_point: QPoint, 
                 coef_px_to_count:list, 
                 count_meter:float,
                 fon_value: float,
                 path_to_np: str) -> None:
        
        self.start_point_count_x = int(start_point.x() * coef_px_to_count[0])
        self.start_point_count_y = int(start_point.y() * coef_px_to_count[1])
        self.end_point_count_x = int(end_point.x() * coef_px_to_count[0])
        self.end_point_count_y = int(end_point.y() * coef_px_to_count[1])
        self.path_to_np = path_to_np
    
        self.fon_value = fon_value
        self.count_meter = count_meter

        self.solve()

    def solve(self) -> None:
        count = self.bresenham_line_points()
        ampl_values = self.get_ampl_values_along_line(count)
        self.get_graph(ampl_values)

    def bresenham_line_points(self) -> list:
        # Реализация алгоритма линейной интерполяции Брезенхема для получения координат
        points = []
        x0 = self.start_point_count_x
        y0 = self.start_point_count_y
        x1 = self.end_point_count_x
        y1 = self.end_point_count_y
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return points

    def get_ampl_values_along_line(self, line_points: list) -> list:
        image = np.load(self.path_to_np)
        # Получение значений пикселей из изображения на каждой точке линии
        ampl_values = []
        for x, y in line_points:
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                ampl_values.append(image[y, x])  # Примечание: Порядок (y, x) для массивов NumPy

        return ampl_values

    def get_graph(self, ampl_values):

        # Создайте ось x, представляющую позиции вдоль линии (индексы пикселей)
        x_axis = np.arange(len(ampl_values))
        # Преобразуйте список 'ampl_values_along_line' в массив NumPy для построения графика
        ampl_values_np = np.array(ampl_values)
        # Сглаживание графика с помощью скользящего среднего
        if len(ampl_values)>100:
            window_size = len(ampl_values)//100
            ampl_values_np = np.convolve(ampl_values_np, np.ones(window_size)/window_size, mode='same')


        mean_array = np.mean(ampl_values_np).astype(float)

        plt.ion()

        plt.figure(num='Амплитудные характеристики изображения', dpi=80, facecolor='w', edgecolor='k', tight_layout=True)
        plt.clf()  # Очистить предыдущий график

        # редактирование значков
        toolbar = plt.get_current_fig_manager().toolbar # type: ignore
        unwanted_buttons = ["Home", "Back", "Forward", "Pan", "Zoom", "Subplots", "Customize"]

        for x in toolbar.actions():
            if x.text() == "Save":
                x.setToolTip("Сохранить график")
            if x.text() in unwanted_buttons:
                toolbar.removeAction(x)

        # установка иконки
        pixmap = QPixmap(':/ico/qt_forms/resources/icon.png')
        plt.get_current_fig_manager().window.setWindowIcon(QIcon(pixmap)) # type: ignore

        # Постройте значения пикселей в виде графика
        plt.plot(x_axis, ampl_values_np)

        # Максимальное значение новой метки
        max_new_tick = self.count_meter

        # Генерация равномерных меток
        num_ticks = 10  # Количество меток, включая начальное и конечное значение
        new_xticks = np.linspace(0, max_new_tick, num_ticks)
        old_xticks = np.linspace(0, len(ampl_values), num_ticks)
        new_xtick_labels = [str(int(value)) for value in new_xticks]  # Преобразование в строку

        # Установка новых меток на оси X
        plt.xticks(old_xticks, new_xtick_labels)

        # Настройте внешний вид графика (при необходимости)
        plt.xlabel('Расстояние, м.')
        plt.ylabel('Абсолютные амплитудные значения')
        plt.grid(True)
        
        # Добавляем горизонтальную линию фона
        plt.axhline(self.fon_value, color='red', label='Среднее значение фона')
        plt.axhline(mean_array, color='black', label='Среднее значение графика')
        # Добавляем легенду
        plt.legend()
        # Отобразите график
        plt.show()







if __name__ == "__main__":
    pass
