import cv2
import numpy as np

# Предположим, что у вас есть изображение с именем "image.jpg"
image = cv2.imread("output.png", 0)  # Загрузка изображения в оттенках серого

# Применение адаптивного гистограммного выравнивания
clahe = cv2.createCLAHE(clipLimit=20.0, tileGridSize=(8, 8))  # Создание объекта адаптивного гистограммного выравнивания
adjusted_image = clahe.apply(image)  # Применение адаптивного гистограммного выравнивания к изображению

# Сохранение откорректированного изображения
cv2.imwrite("adjusted_image.png", adjusted_image)