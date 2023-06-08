
"""Модуль производит свертку голограммы по дальности.

Исходными данными являются:
Ndn - количество комплексных отсчетов;
Nazim - количество зарегистрированных импульсов;
fcvant - частота дискретизации АЦП;
lamb - длина волны;
Tpi - период повторения импульсов;
Fsp - ширина спектра сигнала;
Dimp - длительность импульса;

file_path - путь до файла голограммы;
file_name - название файла голограммы (опционально);

movement_speed - скорость движения
"""
import numpy as np
import scipy as sc
from scipy import io
import matplotlib.pyplot as plt
from typing import Tuple
import matplotlib.colors as mcolors

class Convolution():
    def __init__(self,
                 Ndn: int,
                 Nazim,
                 fcvant,
                 lamb,
                 Tpi,
                 Fsp,
                 Dimp,
                 file_path: str,
                 file_name: str = '',
                 movement_speed: int = 108, # скорость носителя
                 full_RGG:bool = True,
                 ChKP_param: list =[] , # список параметров ЧКП вида []
                 ) -> None:
        self.file_path = file_path
        self.ChKP_param = ChKP_param
        self.impactChPK = True if self.ChKP_param else False
        self.full_RGG = full_RGG
        self.path_output_rpt:str = self.get_path_output_rpt()

        # для ЧПК они повторяются 
        self.N_otst = 40000 # количество импульсов пропускаемых при чтении РГГ
        self.Na = 90000

        self.Ndn:int = Ndn # количество комплексных отсчетов
        self.Nazim:int = Nazim # количество зарегистрированных импульсов
        self.fcvant:int = fcvant # частота дискретизации АЦП
        self.lamb:float = lamb # длина волны
        self.Tpi:float = Tpi # период повторения импульсов
        self.Fsp:int = Fsp # ширина спектра сигнала
        self.Dimp:float = Dimp # длительность импульса
        self.file_path:str = file_path # путь до файла РГГ
        self.file_name:str = file_name # название файла РГГ (опционально)
        self.movement_speed:float = movement_speed # скорость движения носителя
        self.AntX:float = 0.23 # размер антенны по азимуту
        self.R:int = 4180 # наклонная дальность (до объекта прикрытия)

        '''------------------------Рассчитываемые переменные-------------------------------'''
        self.power_two: int = 2**Ndn.bit_length() # наибольшая степени двойки для отсчетов
        self.dnr:float = 3e8/(2*self.fcvant) # шаг по дальности
        self.dx:float = self.movement_speed*self.Tpi # Шаг по азимуту
        self.Qx:float = self.lamb/self.AntX # ширина ДНА по азимутуD
        self.QRm:float = self.Qx*self.R #  мгновенно облучаемый участок на дальности R, [м] 
        self.QR:int = int(np.fix(self.QRm/self.dx/2)*2) # мгновенно облучаемый участок на дальности R, [отсчет]
        self.resolution_r:float = 3e8/(2*self.Fsp) # разрешение по наклонной дальности, м 
        self.resolution_x:float = 3e8/(2*self.Fsp) # разрешение по азимуту, м 
        self.Nas:int = int(np.fix((np.fix(self.lamb*self.R/2/self.resolution_x/self.dx))/2)*2) # расчет интервала синтезирования
        self.Las:float = self.Nas*self.dx # общая ширина ДНА, которая представляет собой пространственную область или объем, охватываемый радарным излучением или приемом в горизонтальной плоскости
        '''------------------------Инициализация ЧКП-------------------------------'''
        self.ChKP = self.ChKP_builder(self.ChKP_param, self)

    def get_path_output_rpt(self) -> str:
        if self.full_RGG:
            # создание имени файла в зависимости от необходимой свертки
            if self.impactChPK:
                # фаил с результатами свертки по дальности суммарной РГГ (РГГ + ЧКП)
                output_file_path = f"{self.file_path[:-4]}_with_{len(self.ChKP_param)}ChKP.rpt"
            else:
                # фаил с результатами свертки по дальности только исходной РГГ 
                output_file_path = f"{self.file_path[:-4]}.rpt"
        else:
            # фаил с результатами свертки по дальности только ЧКП
            output_file_path = f"{self.file_path[:-4]}_only_ChKP.rpt"
        
        return output_file_path



    def get_support_functions(self) -> None:

        # получение первой опорной функции
        support_function_1 = np.zeros(self.power_two, dtype=np.complex128)
        # число отсчетов в импульсе
        number_pulse_readings = round(
            self.Dimp*self.fcvant)
        for i in range(number_pulse_readings):
            # выражение для расчета фазы первой опорной функции
            phase = np.pi * self.Fsp * \
                (i)**2/(number_pulse_readings*self.fcvant) - \
                np.pi*self.Fsp*(i)/self.fcvant
            # отсчет фазы сигнала в комплексном виде [cos(phase) + sin(phase)j]
            complex_value = complex(np.cos(phase), np.sin(phase))
            support_function_1[i] = complex_value

        # вторая опорная функция
        support_function_2 = np.zeros((self.power_two), dtype=np.complex128)
        # число отсчетов в импульсе
        number_pulse_readings = round(number_pulse_readings/2)
        # сдвиг опорной функции для совмещения начала изображения (кадра)
        # с началом отсчетов
        for i in range(number_pulse_readings):
            support_function_2[i] = support_function_1[i+number_pulse_readings]
            support_function_2[i+self.power_two -
                               number_pulse_readings] = support_function_1[i]
        # применение БПФ к опорной функции
        support_function_2 = support_function_2
        self.ftt_support_function_2 = sc.fft.fft(support_function_2)
        '''
        # вывод полученных графиков
        plt.figure()
        plt.plot(ftt_support_function)
        plt.show()
        plt.figure()
        plt.plot(abs(ftt_support_function_2))
        plt.show()
        '''
        
    def range_convolution(self):
        # создание уточнить
        svRG = stc = np.zeros(self.power_two, dtype=np.complex128)
        # открытие файла голограммы
        with open(self.file_path, 'rb') as rgg_file:
            # поиск начала считывания информации
            rgg_file.seek(2*self.Ndn*self.N_otst, 0)
            # создание временного нового файла для свертки по вертикали
            new_file_path = self.file_path[:-3]+'rpt'
            with open(new_file_path, 'w') as rpt_file:
                for i in range(self.Na): 
                    # чтение фрейма файла
                    new_part_rgg_file = np.frombuffer(rgg_file.read(
                        2*self.Ndn), dtype='uint8')
                    # создание копии из буфера для возможности его редактирования
                    new_part_copy = new_part_rgg_file.copy()
                    # очистка буфера
                    del new_part_rgg_file
                    # формирование значений от -127 до +128 изменением формата
                    new_part_copy = new_part_copy.astype('int8')
                    # заполнение первых 128 значений нулем
                    new_part_copy[:128] = 0
                    # из удвоенного количества отсчетов дальности создается матрица в комплексном виде
                    for i in range(self.Ndn):
                        stc[i] = complex(new_part_copy[2*i],
                                        new_part_copy[2*i+1])
                    stc[self.Ndn:self.power_two] = 0
                    fft_stc = sc.fft.fft(stc)
                    # создание свертки комплексного столбца и опорной функции
                    svRG = fft_stc*self.ftt_support_function_2
                    svRG = sc.fft.ifft(svRG)
                    # создание фрейма для записи
                    write_frame = np.zeros(2*self.power_two)
                    write_frame[0:self.power_two] = svRG.real
                    write_frame[self.power_two:2*self.power_two] = svRG.imag
      
    def azimuth_convolution_ChKP(self, 
                                 ROI:list = [], # область РГГ, которая будет сворачиватся по азимуту в РЛИ
                                 path_input_rpt:str = ''
                                ):
        if ROI:
            # если область задана, то производится распаковка параметров
            N_otst_r, N_otst_y, Na, Ndrz  = ROI
        else:
            # если область не задана, то она равна всей РГГ
            N_otst_r = N_otst_y = 0
            Na = self.Na
            Ndrz = self.Ndn
        '''------------------------ROI--------------------
                     ---->|N_otst_r
                |   +-----|------------------------------+
                |   |.....|..............................|
                v___|_____|____Na_____...................|
            N_otst_y|.....|///////////|..................|
                    |.....|///////////|Ndrz..............|
                    |.....|///////////|..................|
                    |....................................|
                    +------------------------------------+
        '''
        if not path_input_rpt:
            # если путь не введен, то по умолчанию используется путь сохраненный при сворачивании по дальности
            path_input_rpt = self.path_output_rpt
        # предварительное выделение памяти для массива свертки РГГ
        rgg1 = np.empty((Ndrz, Na), dtype=np.complex128)

        with open(path_input_rpt, 'rb') as fid1:
            fid1.seek(2 * self.power_two * N_otst_r * 4 + N_otst_y * 4)

            for i in range(Na):
                r1 = np.fromfile(fid1, dtype=np.float32, count=Ndrz)
                fid1.seek((self.power_two - Ndrz) * 4, 1)
                r2 = np.fromfile(fid1, dtype=np.float32, count=Ndrz)
                fid1.seek((self.power_two - Ndrz) * 4, 1)
                rgg1[:, i] = r1 + 1j * r2
            
    
        """plt.figure()
        plt.imshow(abs(np.real(rgg1)), cmap='gray', aspect='auto')
        plt.title('РГГ суммарная')
        plt.show()"""
        Ndrz0, Na0 = rgg1.shape # Определение размеров массива РГГ
        # определение минимальной наклонной дальности на изображении
        R_UO = self.R
        #TODO: Фиксировано ли значение
        N_UO = 714 #  Номер строки в нашем РЛИ с УО на дальности R_UO
        Rmin = R_UO - (N_UO - 1) * self.dnr
        Rmax = Rmin + Ndrz * self.dnr
        alfa = self.get_drift_angle(rgg1,R_UO,self.dx,self.lamb, Na0)
        # Расчет N_snos_x
        N_snos_x = np.round(np.tan(np.deg2rad(alfa)) * Rmin / self.dx).astype(int)
        dsm0 = N_snos_x
        # определение предельной величины высоты блока в метрах
        Ls_sr = np.round(lamb * Rmin / (2 * self.resolution_x)).astype(int)
        # Расчет dR
        dR = self.lamb * (R_UO / (Ls_sr + 2 * np.abs(N_snos_x) * self.dx)) ** 2
        #TODO: Фиксировано ли значение
        # Высота блока в отсчетах (по изображению)
        Ndr = 2
        # Количество разбиений (блоков) по наклонной дальности
        Nbl_r = np.round(Ndrz0 / Ndr).astype(int)

        # инициализация переменных для цикла
        # Задание alfa0 TODO: так альфа не нужен
        alfa0 = [0]
        # закладка на будущий цикл TODO: как определяется alfa_count и Vi_count! 
        alfa_count = 1  
        dsm_bl = np.zeros((Nbl_r, alfa_count), dtype=int)
        # ----------------------------------

        for Nugol in range(alfa_count):
            alfa = alfa0[Nugol]
            # Если на всех дальностях снос не изменять !!!
            N_snos_x_bl = int(np.round(np.tan(np.deg2rad(alfa)) * R_UO / self.dx))  

            # инициализация переменных для цикла
            Vi_count = 1 
            Vi = np.zeros(Vi_count, dtype=int)
            # ----------------------------------
            for j in range(Vi_count):
                Vi[j] = self.movement_speed

                # инициализация переменных для цикла
                R_cb = Las_bl = np.zeros(Nbl_r)
                RLI1 = np.empty((Ndrz, Na), dtype=np.complex128)
                # ----------------------------------

                for i in range(Nbl_r):
                    if Nbl_r == 1:
                        R_centr_bl = R_UO
                        Ndr = Ndrz0
                    else:
                        # Наклонная дальность до центра блока в метрах
                        R_centr_bl = Rmin + ((i+1) * Ndr - Ndr / 2) * self.dnr  
  
                    R_cb[i] = R_centr_bl

                    Nas_bl:int = int((lamb * R_centr_bl) // (2 * self.resolution_x * self.dx))
                    Nas_bl = (Nas_bl // 2) * 2

                    if alfa == 0:
                        N_snos_x_bl = 0
                    else:
                        pass  # Здесь нужно добавить соответствующие вычисления для N_snos_x_bl

                    dsm = -N_snos_x_bl
                    dsm_bl[i, Nugol] = dsm

                    Las_bl = Nas_bl * self.dx 
                    x_max = Las_bl / 2 + abs(N_snos_x_bl) * self.dx
                    rt1_max_bl = np.sqrt(R_centr_bl ** 2 + x_max ** 2) - R_centr_bl
                    dop_Ndr = int(np.round(rt1_max_bl / self.dnr))
                   
                    if dop_Ndr > Ndrz0 - (i+1) * Ndr:
                        dop_Ndr = Ndrz0 - (i+1) * Ndr
                    elif dop_Ndr < 0:
                        raise ValueError("Величина dop_Ndr не может быть меньше нуля")

                    Ndr_bl = Ndr + dop_Ndr
                    rgg1_bl = rgg1[i * Ndr:(i+1) * Ndr + dop_Ndr, :]
                    #rgg2_bl = rgg2[(Y-1) * Ndr:Y * Ndr + dop_Ndr, :]

                    #OF1_bl = np.zeros(Nas_bl)
                    OF2_bl = np.zeros((Ndr_bl, Nas_bl), dtype=np.complex128)

                    x = np.arange(-Nas_bl / 2 + dsm, Nas_bl / 2 + dsm) * self.dx
                    rt = np.sqrt(R_centr_bl ** 2 + x ** 2)
                    rt1 = rt - R_centr_bl
                    N0_bl = np.floor(rt1 / self.dnr).astype(int)
                    phase = -4 * np.pi * rt / lamb
                    OF1_bl = np.cos(phase) + 1j * np.sin(phase)
                    OF2_bl[N0_bl, np.arange(Nas_bl)] = OF1_bl
                    

                    OF_bl = np.zeros((Ndr_bl, Na0), dtype=np.complex128)
                    Ndr_OF, Na_OF = OF2_bl.shape

                    if Ndr_OF > Ndr_bl:
                        OF2_bl = OF2_bl[:Ndr_bl, :]

                    if Na0 / 2 < Nas_bl / 2 + abs(dsm):
                        raise ValueError("Не выполняется условие Na0/2 >= Nas_bl/2 + dsm")

                    OF_bl[:, int(Na0 / 2 - Nas_bl / 2 + dsm):int(Na0 / 2 + Nas_bl / 2 + dsm)] = OF2_bl

                    sp_rgg1_bl = np.fft.fft2(rgg1_bl)
                    #sp_rgg2_bl = np.fft.fft2(rgg2_bl)
                    sp_OF_bl = np.fft.fft2(OF_bl)

                    RLI1_bl = sp_rgg1_bl * np.conj(sp_OF_bl)
                    #RLI2_bl = sp_rgg2_bl * np.conj(sp_OF_bl)

                    RLI1_bl = np.abs(np.fft.ifft2(RLI1_bl))
                    #RLI2_bl = np.abs(np.fft.ifft2(RLI2_bl))

                    RLI1[i * Ndr:(i+1) * Ndr, :] = RLI1_bl[:Ndr, :]
                    #RLI2[(Y-1) * Ndr:Y * Ndr, :] = RLI2_bl[:Ndr, :]
  
    
                RLI1 = np.fft.fftshift(RLI1, axes=1)
                #RLI2 = np.fft.fftshift(RLI2, axes=1)

                Ny2 = [705, 725]
                Nx2 = [2400, 2700]
                UO = RLI1[Ny2[0]:Ny2[1], Nx2[0]:Nx2[1]]

                # Вызов функции опр-я разрешения по УО и координат Максимума
                # fig = plt.figure()
                # [razr_x[Qv, Nugol], razr_y[Qv, Nugol], Amp[Qv, Nugol], Nx02[Qv, Nugol],
                # Ny02[Qv, Nugol]] = Funct_razr_po_UO(UO, dnr, dx, Nx2, Ny2, V, alfa)




                plt.figure()
                plt.imshow(np.abs(RLI1), cmap='gray',  aspect='auto', norm=mcolors.PowerNorm(0.3))
                plt.title(f'АРЛИ сформированное по суммарной РГГ {ROI}')
                plt.show()
                # plt.plot([Nx02[Qv, Nugol] - 1, Nx02[Qv, Nugol] + 1], [Ny02[Qv, Nugol] - 1, Ny02[Qv, Nugol] + 1], 'r', linewidth=2)
                # plt.plot([Nx02[Qv, Nugol] - 1, Nx02[Qv, Nugol] + 1], [Ny02[Qv, Nugol] + 1, Ny02[Qv, Nugol] - 1], 'r', linewidth=2)

                # fig = plt.figure()
                # plt.imshow(RLI2 * 0.003, cmap='gray')
                # plt.title('АРЛИ ЧКП')



    def get_drift_angle(self, rgg1 , Rsr:float, dx:float, lamb:float, Na0:int) -> float:
        """
        Определяет снос и угол сноса на основе РГГ.

        Аргументы:
        - rgg1 (np.ndarray): Массив РГГ размером [Ndrz0, Na0].
        - Rsr (float): Средняя дальность для определения сноса.
        - dx (float): Шаг по азимуту.
        - lamb (float): Длина волны.

        Возвращает кортеж с тремя значениями:
        - Ugol_snosa (float): Угол сноса в градусах.
        """

        # Вычисление суммы значений РГГ по строкам и вычитание среднего значения
        rg_sum = np.sum(rgg1, axis=0, dtype=np.complex128)
        sr_rg_sum = np.mean(rg_sum, dtype=np.complex128)
        rg_sum -= sr_rg_sum
        # Применение быстрого преобразования Фурье (БПФ) к сумме РГГ для получения доплеровского спектра
        srgg1 = np.fft.fft(rg_sum)
        Asrgg1 = np.abs(srgg1) # Вычисление амплитудного спектра
        # Сглаживание доплеровского спектра путем обнуления значений за пределами заданного диапазона
        Argg1 = np.fft.ifft(Asrgg1)
        Argg1[10:-10] = 0
        srgg1 = np.fft.fft(Argg1)
        # Определение порогового уровня для оценивания доплеровского сдвига
        srgg1 = np.abs(np.real(srgg1))
        sm = np.max(srgg1)*0.9

        srgg1 = np.where(srgg1 >= sm, 1, 0)
        # Определение среднего доплеровского сдвига a0 на основе порогового уровня
        a1 = a2 = 0
        for i in range(Na0 - 1):
            if srgg1[i] < srgg1[i + 1]:
                a1 = i
            if srgg1[i] > srgg1[i + 1]:
                a2 = i
        if a1 > a2: 
            a2 = a2 + Na0 
        a0 = (a1 + a2) / 2
        if a0 > Na0 / 2:
            a0 = a0 - Na0
        # Вычисление сноса в отсчетах для Rsr и угла сноса в градусах
        N_snos_x = int(a0 / Na0 * lamb * Rsr / (2 * dx ** 2))
        alfa = np.degrees(np.arctan(N_snos_x * dx / Rsr))
     
        return alfa

    def range_convolution_ChKP(self,
                                sumRGGandChKP: bool = True, #если true - формируется суммарная РГГ, если false - то только ЧКП
                                impactChPK: bool = True, # показатель воздействия ЧПК
                                razmer_ChKP_r: int = 100, # размер ЧКП по наклонной дальности
                                razmer_ChKP_x: int = 450, # размер ЧКП по азимуту
                                AmpChkp: int = 25, # мощность ЧПК без размера
                                X_ChKP: int = 8400, #  x координата ЧКП внутри исходной РГГ (в отсчетах)
                                Y_ChKP: int = 3190, # y координата ЧКП внутри исходной РГГ  (в отсчетах)
                                # TODO: откуда берутся данные
                                ) -> None:

            
        # расчет переменных
        Ts = self.Las/self.movement_speed # временной интервал, необходимый для охвата всей ширины ДНА во время движения
        x_max = self.dx*self.QR/2 # количество шагов азимута, которые укладываются в один интервал синтезирования
        rt_max = np.sqrt(self.R**2+x_max**2) # TODO: что за значение?
        ndop_max = int(np.fix((rt_max-self.R)/self.dnr)) # TODO: что за значение?  
        


        if impactChPK:
            # формирование ЛЧМ сигнал для модели РГГ ЧКП
            N1 = int(np.fix(self.Dimp * self.fcvant))# количество дискретных отсчетов в ЛЧМ
            N_razb_r = razmer_ChKP_r/self.resolution_r  # количество разбиений РГГ по дальности
            N_razb_x = razmer_ChKP_x/self.resolution_x # количество разбиений РГГ по азимуту
            Nd_r = int(np.ceil(N1/N_razb_r)) # количество когерентных отсчетов на одном участке разбиения по дальности    
            Nd_x = int(np.ceil(self.Nas/N_razb_x)) # количество когерентных отсчетов на одном участке разбиения по азимуту
            Fakt_razb_r = int(np.ceil(N1/Nd_r)) # Fakt_razb_r может отличаться от N_razb_r на +- 1
            Fakt_razb_x = int(np.ceil(self.QR/Nd_x)) # Для самолета Nas<<QR, следовательно Nd_x<<Fakt_razb_x
            Tau_koger_r = self.Dimp/N_razb_r  # интервал когерентности по дальности
            Tau_koger_x = Ts/N_razb_x  # интервал когерентности по азимуту
            Mdop=0 # TODO: уточнить переменные 
            
            LCHM = np.zeros((N1, 1))
            for n in range(N1):
                LCHM[n,0] = np.pi * self.Fsp * n**2 / (N1 * self.fcvant) - np.pi * self.Fsp * (n) / self.fcvant
            w = 4 * np.pi / lamb
               
            '''
            s = 2
            np.random.seed(s)
            U = (np.random.rand(Fakt_razb_r, Fakt_razb_x) - 0.5) * 2 * np.pi
            '''
            data = io.loadmat('U_rand.mat')
            U = np.array(data['U'])
               
            # Создание массива U_sl0 с нулевыми значениями размера (Nd_r * Fakt_razb_r, Fakt_razb_x)
            U_sl0 = np.zeros((Nd_r * Fakt_razb_r, Fakt_razb_x))

            # Заполнение массива U_sl0 значениями из U, повторяя каждое значение Nd_r раз по оси 0
            for i in range(Fakt_razb_x):
                U_sl0[:, i] = U[:, i].repeat(Nd_r)

            # Обрезка массива U_sl0 до размера N1
            U_sl0 = U_sl0[:N1, :]
            # Создание комплексного массива U_sl0_compl из U_sl0, где вещественная часть - np.cos(U_sl0), мнимая часть - np.sin(U_sl0)
            U_sl0_compl = np.cos(U_sl0) + 1j * np.sin(U_sl0)
            # Вычисление размера Nd_ChKP, округленного вверх до ближайшего четного числа
            Nd_ChKP = int(np.ceil((N1 + ndop_max + 2 * Mdop) / 2)) * 2
            Nd_ChKP = int(np.ceil(Nd_ChKP / 2)) * 2
            # Создание комплексного массива Rgg_ChKP нулей размера (Nd_ChKP, QR)
            Rgg_ChKP = np.zeros((Nd_ChKP, self.QR), dtype=np.complex128)
            # Создание массива ndop нулей размера QR для хранения индексов
            ndop = np.zeros(self.QR, dtype=int)
            # Вычисление значений массива ndop и заполнение массивов Imp и U_sl
            for i in range(self.QR):
                U_sl = np.zeros((Nd_ChKP,1), dtype=complex)
                Imp = np.zeros((Nd_ChKP,1), dtype=complex)
                x = (-self.QR / 2 + i) * self.dx
                rt = np.sqrt(self.R ** 2 + x ** 2)
                ndop[i] = int(np.fix((rt - self.R) / self.dnr))
                phase = LCHM + w * rt
                Imp0 = np.sin(phase) + 1j * np.cos(phase)
                Imp[ndop[i] + Mdop:ndop[i] + Mdop + N1] = Imp0
                qq = i // Nd_x
                U_sl[ndop[i] + Mdop:ndop[i] + Mdop + N1,0] = U_sl0_compl[:, qq]
                # Заполнение Rgg_ChKP значением Imp * U_sl
                Rgg_ChKP[:, i] = np.squeeze(Imp * U_sl)

            Rgg_ChKP *= AmpChkp
            # Получение размеров Y0 и X0 массива Rgg_ChKP
            Y0, X0 = Rgg_ChKP.shape
          
            Rgg_ChKP2 = np.zeros((self.power_two, X0), dtype=np.complex128)
            Rgg_ChKP2[Y_ChKP:Y0 + Y_ChKP, :] = Rgg_ChKP
            print(Rgg_ChKP2[6231,6063])

            del U, U_sl0_compl, Rgg_ChKP


            # ====== Формирование ОФ для свертки зондирующего импульса ============
            N2 = N1 // 2
            opor_func_1 = np.zeros((self.power_two, 1), dtype=np.complex128)
            opor_func_1[:N1] = np.cos(LCHM) + 1j * np.sin(LCHM) # фаза сигнала в комплексном виде
            opor_func_2 = np.zeros((self.power_two, 1), dtype=np.complex128)
            
            opor_func_2[:N2] = opor_func_1[N2:N1]                
            opor_func_2[self.power_two-N2:self.power_two] = opor_func_1[:N2]
            # ftt работает только со строкой, поэтому производится транспонирование
            sp_OF = np.fft.fft(opor_func_2.T)

            del opor_func_1, opor_func_2, LCHM # массивы opor, opor1, opor2, LCHM удаляются, чтобы освободить память

            svRG = np.zeros((self.power_two,1), dtype=np.complex128)  # Инициализация массива размером Nd с нулями
            

            # открытие файла голограммы и файла для записи свертки по дальности
            with open(self.file_path, 'rb') as rgg_file, open(self.path_output_rpt, 'wb') as rpg_file:
                # установка начала считывания голограммы
                rgg_file.seek(2*self.Ndn*self.N_otst, 0)          
                
                if sumRGGandChKP:
                    # счетчик столбцов РГГ 
                    ChKP_column_count = 0
                    for i in range(self.Na):
                        # значение считываются в диапазоне от -127 до +128
                        st = np.fromfile(rgg_file, dtype=np.int8, count=Ndn*2) 
                        # заполнение первых 128 значений нулем
                        st[:128] = 0                    
                        # Преобразование удвоенного количества отсчетов в столбец комплексных чисел
                        stc = st[::2] + 1j * st[1::2]
                        # добавление нулей в конец массива 
                        stc = np.concatenate((stc, np.zeros(self.power_two - len(stc), dtype=np.complex128)))  # Добавление нулевых элементов

                        if impactChPK and X_ChKP - X0/2 < i + 1 <= X_ChKP + X0/2:
                            # добавление в столбцы исходной РГГ столбцов РГГ ЧКП 
                            stc += Rgg_ChKP2[:, ChKP_column_count]
                            ChKP_column_count += 1
                                           
                        fft_stc = np.fft.fft(stc)
                        # создание свертки комплексного столбца и опорной функции
                        svRG = fft_stc*sp_OF
                        svRG = np.fft.ifft(svRG)
                        # создание фрейма для записи
                        write_frame = np.zeros(2*self.power_two)
                        write_frame[0:self.power_two] = svRG.real
                        write_frame[self.power_two:2*self.power_two] = svRG.imag
                        write_frame.astype(np.float32).tofile(rpg_file)  # Запись в файл

                else:
                    for i in range(X0):
                        stc = Rgg_ChKP2[:, i]

                 
                        sp_stc = np.fft.fft(stc.T)
                      
                        svRG = sp_stc* sp_OF  # Умножение спектров столбца на опорную функцию
                        svRG = np.fft.ifft(svRG)
                        Rg = np.concatenate((np.real(svRG), np.imag(svRG)))
                        Rg.astype(np.float32).tofile(rpg_file)  # Запись в файл
                      

    class ChKP_builder():
        def __init__(self, ChKPs_param: list, parent) -> None:
            """Класс принимает параметры:
            ChKP_param: [[]]
                ChKP_size_r - размер ЧКП по наклонной дальности;
                ChKP_size_x - размер ЧКП по азимуту;
                Chkp_power - мощность ЧПК [без размера];
                ChKP_location_x - координата x ЧКП внутри исходной РГГ [отсчеты];
                ChKP_location_y - координата у ЧКП внутри исходной РГГ [отсчеты].
            parent: ссылка на родительский класс
            """
            self.ChKPs_param = ChKPs_param
            # инициализация переменных родительского класса
            self.RSA_param = parent
            '''------------------------Рассчитываемые переменные-------------------------------'''
            self.Ts = self.RSA_param.Las/self.RSA_param.movement_speed # временной интервал, необходимый для охвата всей ширины ДНА во время движения
            self.x_max = self.RSA_param.dx*self.RSA_param.QR/2 # количество шагов азимута, которые укладываются в один интервал синтезирования
            self.rt_max = np.sqrt(self.RSA_param.R**2+self.x_max**2) # TODO: что за значение?
            self.ndop_max = int(np.fix((self.rt_max-self.RSA_param.R)/self.RSA_param.dnr)) # TODO: что за значение? 
            self.N1 = int(np.fix(self.RSA_param.Dimp * self.RSA_param.fcvant))# количество дискретных отсчетов в ЛЧМ
            self.w = 4 * np.pi / self.RSA_param.lamb # TODO: что за значение? 
            # создание массива линейной частотной модуляции
            n = np.arange(self.N1)
            LCHM = np.pi * self.RSA_param.Fsp * n**2 / (self.N1 * self.RSA_param.fcvant) - np.pi * self.RSA_param.Fsp * (n) / self.RSA_param.fcvant
            self.LCHM = LCHM.reshape((self.N1, 1))
         
        def get_ChKP_RGG(self, ChKP_param):
            """Метод производит синтезировать РГГ ЧКП"""           
           
            # распаковка параметров ЧКП
            ChKP_size_r, ChKP_size_x, Chkp_power, ChKP_location_x, ChKP_location_y = ChKP_param
            N_razb_r = ChKP_size_r/self.RSA_param.resolution_r  # количество разбиений РГГ по дальности
            N_razb_x = ChKP_size_x/self.RSA_param.resolution_x # количество разбиений РГГ по азимуту
            Nd_r = int(np.ceil(self.N1/N_razb_r)) # количество когерентных отсчетов на одном участке разбиения по дальности    
            Nd_x = int(np.ceil(self.RSA_param.Nas/N_razb_x)) # количество когерентных отсчетов на одном участке разбиения по азимуту
            Fakt_razb_r = int(np.ceil(self.N1/Nd_r)) # Fakt_razb_r может отличаться от N_razb_r на +- 1
            Fakt_razb_x = int(np.ceil(self.RSA_param.QR/Nd_x)) # Для самолета Nas<<QR, следовательно Nd_x<<Fakt_razb_x
            #--TODO: нужны ли эти переменные?
            #--Tau_koger_r = self.RSA_param.Dimp/N_razb_r  # интервал когерентности по дальности
            #--Tau_koger_x = self.Ts/N_razb_x  # интервал когерентности по азимуту
            Mdop=0
            
            # формирование случайной функции ЧКП
            '''
            np.random.seed(2) # установка начального генератора случайной величины
            U = (np.random.rand(Fakt_razb_r, Fakt_razb_x) - 0.5) * 2 * np.pi
            '''
            data = io.loadmat('U_rand.mat')
            U = np.array(data['U'])

            # создание массива с нулевыми значениями размера 
            U_sl0 = np.zeros((Nd_r * Fakt_razb_r, Fakt_razb_x))

            # Заполнение массива  значениями из U, повторяя каждое значение Nd_r раз по оси 0
            for i in range(Fakt_razb_x):
                U_sl0[:, i] = U[:, i].repeat(Nd_r)
            # обрезка массива
            U_sl0 = U_sl0[:self.N1, :]
            # создание комплексного массива U_sl0_compl из U_sl0, где вещественная часть - np.cos(U_sl0), мнимая часть - np.sin(U_sl0)
            U_sl0_compl = np.cos(U_sl0) + 1j * np.sin(U_sl0)

            # вычисление размера, округленного вверх до ближайшего четного числа
            Nd_ChKP = int(np.ceil((self.N1 + self.ndop_max + 2 * Mdop) / 2)) * 2
            Nd_ChKP = int(np.ceil(Nd_ChKP / 2)) * 2
            # Создание комплексного массива Rgg_ChKP нулей размера (Nd_ChKP, QR)
            Rgg_ChKP = np.zeros((Nd_ChKP, self.RSA_param.QR), dtype=np.complex128)
            # Создание массива ndop нулей размера QR для хранения индексов
            #ndop = np.zeros(self.RSA_param.QR, dtype=int)
            
            indices = np.arange(self.RSA_param.QR)
            x = (-self.RSA_param.QR  / 2 + indices) * self.RSA_param.dx
            rt = np.sqrt(self.RSA_param.R ** 2 + x ** 2)
            phase = self.LCHM + self.w * rt
            ndop = (rt - self.RSA_param.R) // self.RSA_param.dnr
            Imp0 = np.sin(phase) + 1j * np.cos(phase)

            # Вычисление значений массива ndop и заполнение массивов Imp и U_sl
            for i in range(self.RSA_param.QR):
                U_sl = np.zeros((Nd_ChKP,1), dtype=complex)
                Imp = np.zeros((Nd_ChKP,1), dtype=complex)
                Imp[ndop[i] + Mdop:ndop[i] + Mdop + self.N1] = Imp0
                qq = i // Nd_x
                U_sl[ndop[i] + Mdop:ndop[i] + Mdop + self.N1,0] = U_sl0_compl[:, qq]
                # Заполнение Rgg_ChKP значением Imp * U_sl
                Rgg_ChKP[:, i] = (Imp * U_sl).ravel()

            Rgg_ChKP *= Chkp_power
            # Получение размеров Y0 и X0 массива Rgg_ChKP
            Y0, X0 = Rgg_ChKP.shape
        
            Rgg_ChKP2 = np.zeros((self.RSA_param.power_two, X0), dtype=np.complex128)
            Rgg_ChKP2[ChKP_location_y:Y0 + ChKP_location_y, :] = Rgg_ChKP

            return Rgg_ChKP2





        

                              






def write_file_function(stc, sp_OF, name_writing_file):
    sp_stc = np.fft.fft(stc)
    svRG = sp_stc * sp_OF  # Умножение спектров столбца на опорную функцию
    svRG = np.fft.ifft(svRG)
    Rg = np.concatenate((np.real(svRG), np.imag(svRG)))
    Rg.astype(np.float32).tofile(name_writing_file)  # Запись в файл

            

       

if __name__ == '__main__':

    Ndn = 10944+64
    Nazim = 165500
    fcvant = 400e6
    lamb = 0.0351
    Tpi = 485.692e-6
    Fsp = 300e6
    Dimp = 10e-6

    sf = Convolution(Ndn,
                     Nazim,
                     fcvant,
                     lamb,
                     Tpi,
                     Fsp,
                     Dimp,
                     "C:/Users/X/Desktop/185900/1.rgg")

    #sf.get_support_functions()
    #sf.range_convolution()
    #sf.range_convolution_ChKP()
    sf.azimuth_convolution_ChKP([0,4000,20000,2000], 'C:/Users/X/Desktop/185900/sv_185900_ChKP_100m_450m_v2.rpt')
