import numpy as np
import matplotlib.pyplot as plt
from scipy import io

data = io.loadmat('U_rand.mat')
U = np.array(data['U'])
U_sl0 = np.zeros((20 * 200, 3040))
U_sl0 = np.tile(U, (20, 1))
U_sl0_compl = np.cos(U_sl0) + 1j * np.sin(U_sl0)

w = 4 * np.pi / 0.0351
dnr = 3e8/(2*400e6)
N1 = 4000
n = np.arange(N1)
LCHM = np.pi * 300e6 * (n**2 / (N1 * 400e6) - n / 400e6)
LCHM = LCHM.reshape((N1, 1))

dx = 108*485.692e-6 # Шаг по азимуту
QRm:float = 0.0351/0.23*4180 #  мгновенно облучаемый участок на дальности R, [м] 
QR:int = int(np.fix(QRm/dx/2)*2) # мгновенно облучаемый участок на дальности R, [отсчет]

indices = np.arange(QR)
x = (-QR / 2 + indices) * dx
rt = np.sqrt(4180 ** 2 + x ** 2)
phase = LCHM + w * rt
ndop = int(np.fix((rt - 4180) / 3e8/(2*400e6)))
Imp0 = np.sin(phase) + 1j * np.cos(phase)
#ndop = np.zeros(QR, dtype=int)
Rgg_ChKP = np.zeros((QR), dtype=np.complex128)
Mdop = 0
for i in range(QR):
        U_sl = np.zeros((4032,1), dtype=complex)
        Imp = np.zeros((4032,1), dtype=complex)
        #ndop[i] = int(np.fix((rt[i] - 4180) / dnr))
        Imp[ndop[i] + Mdop:ndop[i] + Mdop + N1] = Imp0[i]
        qq = i // 4
        U_sl[ndop[i] + Mdop:ndop[i] + Mdop + N1,0] = U_sl0_compl[:, qq]
        # Заполнение Rgg_ChKP значением Imp * U_sl
        Rgg_ChKP[:, i] = np.squeeze(Imp * U_sl)