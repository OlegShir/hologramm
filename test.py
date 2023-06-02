import numpy as np
import matplotlib.pyplot as plt

N1 = 4000
LCHM = np.zeros((N1, 1))
for n in range(N1):
        LCHM[n,0] = np.pi * 300e6 * n**2 / (N1 * 400e6) - np.pi * 300e6 * (n) / 400e6
Tpi = 485.692e-6

dx = 108*Tpi # Шаг по азимуту
Qx:float = 0.0351/0.23 # ширина ДНА по азимутуD
QRm:float = Qx*4180 #  мгновенно облучаемый участок на дальности R, [м] 
QR:int = int(np.fix(QRm/dx/2)*2) # мгновенно облучаемый участок на дальности R, [отсчет]

# Создание массива индексов от 0 до QR-1
indices = np.arange(QR)

# Вычисление массива x без использования цикла
x = (-QR / 2 + indices) * dx

rt = np.sqrt(4180 ** 2 + x ** 2)



x += 0