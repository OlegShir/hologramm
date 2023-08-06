import numpy as np

import csv

list1 = []
list2 = []

# Открываем файл для чтения в режиме текста
with open('output.csv', 'r', newline='') as csvfile:
    # Создаем объект reader для чтения из файла
    reader = csv.reader(csvfile)
    
    # Пропускаем заголовок
    next(reader)
    
    # Читаем данные из столбцов и добавляем их в списки
    for row in reader:
        item1, item2 = row
        list1.append(int(item1))
        list2.append(float(item2))

# Ваши данные
x_values = np.array(list1)
y_values = np.array(list2)

# Вычисление коэффициентов линейной регрессии
coefficients = np.polyfit(x_values, y_values, 1)
a = coefficients[0]  # Коэффициент наклона (наклон прямой)
b = coefficients[1]  # Коэффициент смещения (пересечение с осью y)

# Уравнение линейной регрессии: y = a * x + b
print(f"Уравнение линейной регрессии: y = {a:.2f} * x + {b:.2f}")