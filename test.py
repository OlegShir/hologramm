import numpy as np
import matplotlib.pyplot as plt



def bresenham_line_points(start_point: list, end_point: list) -> list:
    # Реализация алгоритма линейной интерполяции Брезенхема для получения координат пикселей
    points = []
    x0, y0 = start_point
    x1, y1 = end_point
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

def get_pixel_values_along_line(image: np.ndarray, line_points: list) -> list:
    # Получение значений пикселей из изображения на каждой точке линии
    pixel_values = []
    for x, y in line_points:
        if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
            pixel_values.append(image[y, x])  # Примечание: Порядок (y, x) для массивов NumPy

    return pixel_values

def get_pixel_grafic(pixel_values):
    # Предположим, что у вас есть список 'pixel_values_along_line' с значениями пикселей
    # Создайте ось x, представляющую позиции вдоль линии (индексы пикселей)
    print(len(pixel_values))
    x_axis = np.arange(len(pixel_values))

    # Преобразуйте список 'pixel_values_along_line' в массив NumPy для построения графика
    pixel_values_np = np.array(pixel_values)

    # Постройте значения пикселей в виде графика
    plt.plot(x_axis, pixel_values_np)

    # Настройте внешний вид графика (при необходимости)
    plt.xlabel('Позиция вдоль линии')
    plt.ylabel('Значения пикселей')
    plt.title('Значения пикселей вдоль линии')
    plt.grid(True)

    # Отобразите график
    plt.show()





if __name__ == "__main__":
    # Предполагая, что у вас есть отображаемое изображение в виде массива NumPy с именем 'image_np'
    # и что у вас есть QPoint-объекты 'start_point' и 'end_point'
    # Вы можете использовать следующий код для получения значений пикселей на линии:
    file = "example/example_ROI.flt.npy"

    file_np = np.load(file)
    
    start_point = [200, 600]
    end_point = [250, 890]


    line_points = bresenham_line_points(start_point, end_point)
    pixel_values_along_line = get_pixel_values_along_line(file_np, line_points)
    get_pixel_grafic(pixel_values_along_line)
