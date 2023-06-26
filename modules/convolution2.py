
"""Модуль производит свертку РГГ.
        Аргументы:
        - параметры РСА:
                        [количество комплексных отсчетов, количество зарегистрированных импульсов, частота дискретизации АЦП, длина волны,...
                        период повторения импульсов, ширина спектра сигнала, длительность импульса, скорость движения носителя,...
                        размер антенны по азимуту,наклонная дальность (до объекта прикрытия)]
        - путь до файла *.rgg
        - название файла с которым будет производится сохранение
        - тип обработки
        - параметры ЧКП, если она есть:
                        [[координата x ЧКП внутри исходной РГГ (отсчеты), координата у ЧКП внутри исходной РГГ (отсчеты),
                          мощность ЧПК, размер ЧКП по наклонной дальности, размер ЧКП по азимуту ], [...]...]
        - режим нормализации пикселей РЛИ:
                        "auto" (по умолчанию) - используется геометрическое преобразование
                        "hemming" - используется усреднение Хэмминга
                        "none" - нормализация не производится
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import time, json, datetime, random
from PIL import Image
import cv2

class Convolution():
    def __init__(self,
                 RSA_param:list, #
                 file_path: str, # путь до файла РГГ
                 file_name: str = '', # название файла РГГ (опционально)
                 full_RGG:bool = True, # тип обработки - если True, то обрабатывается вся РРГ, иначе только ЧКП
                 ChKP_param: list =[int] , # список параметров ЧКП вида []
                 auto_px_norm: str = 'auto', # режим нормализации пикселей РЛИ
                 file_path_project: str = '',
                 ) -> None:
        self.start_time = time.time()
        self.ChKP_param = ChKP_param     
        self.full_RGG = full_RGG
        self.file_path:str = file_path # путь до файла РГГ
        self.file_name:str = file_name # название файла РГГ (опционально)  # получение пути для сохранения
        self.auto_px_norm = auto_px_norm
        self.file_path_project = file_path_project
        # для ЧПК они повторяются 
        self.N_otst = 40000 # количество импульсов пропускаемых при чтении РГГ
        self.Na = 90000
        # распаковка параметров РСА
        self.get_init_param_RSA(RSA_param)
        self.impactChPK = False

        '''------------------------Рассчитываемые переменные-------------------------------'''
        self.power_two: int = 2**self.Ndn.bit_length() # наибольшая степени двойки для отсчетов
        self.dnr:float = 3e8/(2*self.fcvant) # шаг по дальности
        self.dx:float = self.movement_speed*self.Tpi # Шаг по азимуту
        self.Qx:float = self.lamb/self.AntX # ширина ДНА по азимутуD
        self.QRm:float = self.Qx*self.R #  мгновенно облучаемый участок на дальности R, [м] 
        self.QR:int = int(np.fix(self.QRm/self.dx/2)*2) # мгновенно облучаемый участок на дальности R, [отсчет]
        self.resolution_r:float = 3e8/(2*self.Fsp) # разрешение по наклонной дальности, м 
        self.resolution_x:float = 3e8/(2*self.Fsp) # разрешение по азимуту, м 
        self.Nas:int = int(np.fix((np.fix(self.lamb*self.R/2/self.resolution_x/self.dx))/2)*2) # расчет интервала синтезирования
        self.Las:float = self.Nas*self.dx # общая ширина ДНА, которая представляет собой пространственную область или объем, охватываемый радарным излучением или приемом в горизонтальной плоскости
        self.N1 = int(np.fix(self.Dimp * self.fcvant)) # количество дискретных отсчетов в ЛЧМ
        # создание массива линейной частотной модуляции
        n = np.arange(self.N1)
        LCHM = np.pi * self.Fsp * n**2 / (self.N1 * self.fcvant) - np.pi * self.Fsp * (n) / self.fcvant
        self.LCHM = LCHM.reshape((self.N1, 1))
        
        # Если ChKP_param пуст - ЧКП нет
        if self.ChKP_param:
            self.impactChPK = True
            # инициализация переменных для класса ChKP_builder
            self.coord_ChKP = []
            self.RGG_ChKP = []
            # счетчик столбцов для ЧКП
            self.ChKP_column_count = np.zeros((len(ChKP_param) ,), dtype=int)
            # инициализация ЧКП
            self.ChKP = self.ChKP_builder(self.ChKP_param, self)
        else:
            self.impactChPK = False 
        self.path_output_rpt:str = self.get_path_output_rpt()

    def get_init_param_RSA(self, RSA_param) -> None:
        """
        Инициализирует распаковку параметров РСА, принимаемых списком из хранилища.
        """
        Ndn, Nazim, fcvant, lamb, Tpi, Fsp, Dimp, movement_speed, AntX, R = RSA_param

        self.Ndn:int = Ndn # количество комплексных отсчетов
        self.Nazim:int = Nazim # количество зарегистрированных импульсов
        self.fcvant:int = fcvant # частота дискретизации АЦП
        self.lamb:float = lamb # длина волны
        self.Tpi:float = Tpi # период повторения импульсов
        self.Fsp:int = Fsp # ширина спектра сигнала
        self.Dimp:float = Dimp # длительность импульса
        self.movement_speed:float = movement_speed # скорость движения носителя
        self.AntX:float = AntX # размер антенны по азимуту
        self.R:int = R # наклонная дальность (до объекта прикрытия)

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
      
    def azimuth_convolution_ChKP(self, 
                                 ROI:list = [], # область РГГ, которая будет сворачиваться по азимуту в РЛИ
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


        # вставка для случая если сворачивается ТОЛЬКО РГГ ЧКП
        # if self.coord_ChKP:
        #     pass

        with open(path_input_rpt, 'rb') as fid1:
            fid1.seek(2 * self.power_two * N_otst_r * 4 + N_otst_y * 4)

            for i in range(Na):
                r1 = np.fromfile(fid1, dtype=np.float32, count=Ndrz)
                fid1.seek((self.power_two - Ndrz) * 4, 1)
                r2 = np.fromfile(fid1, dtype=np.float32, count=Ndrz)
                fid1.seek((self.power_two - Ndrz) * 4, 1)
                rgg1[:, i] = r1 + 1j * r2
       
        Ndrz0, Na0 = rgg1.shape # Определение размеров массива РГГ
        # определение минимальной наклонной дальности на изображении
        R_UO = self.R
        #TODO: Фиксировано ли значение
        N_UO = 714 #  Номер строки в нашем РЛИ с УО на дальности R_UO
        Rmin = R_UO - (N_UO - 1) * self.dnr
        alfa = self.get_drift_angle(rgg1,R_UO, Na0)
        # Расчет N_snos_x
        N_snos_x = np.round(np.tan(np.deg2rad(alfa)) * Rmin / self.dx).astype(int)
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

                    Nas_bl:int = int((self.lamb * R_centr_bl) // (2 * self.resolution_x * self.dx))
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
                    OF2_bl = np.zeros((Ndr_bl, Nas_bl), dtype=np.complex128)

                    x = np.arange(-Nas_bl / 2 + dsm, Nas_bl / 2 + dsm) * self.dx
                    rt = np.sqrt(R_centr_bl ** 2 + x ** 2)
                    # rt1 = rt - R_centr_bl
                    # N0_bl = (rt1 // self.dnr).astype(int)
                    phase = -4 * np.pi * rt / self.lamb
                    OF1_bl = np.cos(phase) + 1j * np.sin(phase)
                    OF2_bl[:Ndr_bl, np.arange(Nas_bl)] = OF1_bl
                    

                    OF_bl = np.zeros((Ndr_bl, Na0), dtype=np.complex128)
                    # Ndr_OF, Na_OF = OF2_bl.shape

                    # if Ndr_OF > Ndr_bl:
                    #     OF2_bl = OF2_bl[:Ndr_bl, :]

                    if Na0 / 2 < Nas_bl / 2 + abs(dsm):
                        raise ValueError("Не выполняется условие Na0/2 >= Nas_bl/2 + dsm")

                    OF_bl[:, int(Na0 / 2 - Nas_bl / 2 + dsm):int(Na0 / 2 + Nas_bl / 2 + dsm)] = OF2_bl
                    sp_OF_bl = np.fft.fft2(OF_bl)

                    rgg1_bl = rgg1[i * Ndr:(i+1) * Ndr + dop_Ndr, :]
                    sp_rgg1_bl = np.fft.fft2(rgg1_bl)
                    RLI1_bl = sp_rgg1_bl * np.conj(sp_OF_bl)
                    RLI1_bl = np.abs(np.fft.ifft2(RLI1_bl))
                    RLI1[i * Ndr:(i+1) * Ndr, :] = RLI1_bl[:Ndr, :]
                    
                    # rgg2_bl = rgg2[i * Ndr:(i+1) * Ndr + dop_Ndr, :]
                    # sp_rgg2_bl = np.fft.fft2(rgg2_bl)
                    # RLI2_bl = sp_rgg2_bl * np.conj(sp_OF_bl)
                    # RLI2_bl = np.abs(np.fft.ifft2(RLI2_bl))
                    # RLI2[i * Ndr:(i+1) * Ndr, :] = RLI2_bl[:Ndr, :]
  
                # АРЛИ суммарной РГГ
                RLI1 = np.fft.fftshift(RLI1, axes=1)
                # АРЛИ ЧКП
                #RLI2 = np.fft.fftshift(RLI2, axes=1)
                print(f'РГГ свернута по азимуту, время: {np.round(time.time()-self.start_time, 2)} c.')
                aspect = 'auto'
                # Нормализации пикселей РЛИ
                if self.auto_px_norm == 'auto':
                    aspect = Na/Ndrz
                elif self.auto_px_norm == 'hemming':
                    # TODO: организовать ввод значений
                    px = 0.25
                    razr_treb_x = razr_treb_y = 0.5 # Требуемое разрешение по азимуту и дальности
                    RLI1 = self.hamming_averaging(RLI1, px, razr_treb_x, razr_treb_y)
                elif self.auto_px_norm == 'none':
                    pass
       
                # сохранение файла описания
                self.save_prj_json()
                self.save_RLI_PIL(RLI1)
                # сохранение РЛ изображения
                # self.save_RLI(RLI1, aspect)

    def save_RLI_PIL(self, RLI):

        # Вычисление амплитуды (модуля) комплексных чисел
        amplitude_values = np.abs(RLI)

        # Применение автоматической коррекции яркости
        min_value = np.min(amplitude_values)
        max_value = np.max(amplitude_values)
        adjusted_values = (amplitude_values - min_value) / (max_value - min_value) * 255

        # Округление значений и преобразование в тип данных uint8
        adjusted_values = adjusted_values.astype(np.uint8)

        # Создание объекта Image с градациями серого
        image = Image.fromarray(adjusted_values, mode='L')

        # Сохранение изображения
        image.save(f"{self.file_path[:-4]}.png")
        
        # Предположим, что у вас есть изображение с именем "image.jpg"
        image = cv2.imread(f"{self.file_path[:-4]}.png", 0)  # Загрузка изображения в оттенках серого

        # Применение адаптивного гистограммного выравнивания
        clahe = cv2.createCLAHE(clipLimit=18.0, tileGridSize=(8, 8))  # Создание объекта адаптивного гистограммного выравнивания
        adjusted_image = clahe.apply(image)  # Применение адаптивного гистограммного выравнивания к изображению

        # Сохранение откорректированного изображения
        cv2.imwrite(f"{self.file_path[:-4]}.png", adjusted_image)


    def save_RLI(self, RLI, aspect, param:list=[])->None:
        if param:
            pass
                        
        # Задание параметров для отображения
        cmap = 'gray'
        #aspect = 'equal'
        norm = mcolors.PowerNorm(0.3)
        # Создание фигуры и осей
        fig, ax = plt.subplots()

        # Отображение радиолокационного изображения
        ax.imshow(np.abs(RLI), cmap=cmap)
        ax.axis('off')  # Убираем отображение осей

        # Сохранение изображения внутри осей
        plt.savefig(f'png/rli{str(datetime.datetime.now().microsecond)}.png', dpi=2000, bbox_inches='tight',  pad_inches=0, format='png')


    def get_drift_angle(self, rgg1 , Rsr:float, Na0:int) -> float:
        """
        Определяет снос и угол сноса на основе РГГ.

        Аргументы:
        - rgg1 (np.ndarray): Массив РГГ размером [Ndrz0, Na0].
        - Rsr (float): Средняя дальность для определения сноса.

        Возвращает кортеж с тремя значениями:
        - alfa (float): Угол сноса в градусах.
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
        N_snos_x = int(a0 / Na0 * self.lamb * Rsr / (2 * self.dx ** 2))
        alfa = np.degrees(np.arctan(N_snos_x * self.dx / Rsr))
     
        return alfa

    def range_convolution_ChKP(self) -> None:

            
        # расчет переменных
        x_max = self.dx*self.QR/2 # количество шагов азимута, которые укладываются в один интервал синтезирования
        # ====== Формирование ОФ для свертки зондирующего импульса ============
        N2 = self.N1 // 2
        opor_func_1 = np.zeros((self.power_two, 1), dtype=np.complex128)
        opor_func_1[:self.N1] = np.cos(self.LCHM) + 1j * np.sin(self.LCHM) # фаза сигнала в комплексном виде
        opor_func_2 = np.zeros((self.power_two, 1), dtype=np.complex128)
        
        opor_func_2[:N2] = opor_func_1[N2:self.N1]                
        opor_func_2[self.power_two-N2:self.power_two] = opor_func_1[:N2]
        # ftt работает только со строкой, поэтому производится транспонирование
        sp_OF = np.fft.fft(opor_func_2.T)
        svRG = np.zeros((self.power_two,1), dtype=np.complex128)  # Инициализация массива размером Nd с нулями
        
        # открытие файла голограммы и файла для записи свертки по дальности
        with open(self.file_path, 'rb') as rgg_file, open(self.path_output_rpt, 'wb') as rpg_file:
            # установка начала считывания голограммы
            rgg_file.seek(2*self.Ndn*self.N_otst, 0)          
            
            if self.full_RGG:
                for i in range(self.Na):
                    # значение считываются в диапазоне от -127 до +128
                    st = np.fromfile(rgg_file, dtype=np.int8, count=self.Ndn*2) 
                    # заполнение первых 128 значений нулем
                    st[:128] = 0                    
                    # Преобразование удвоенного количества отсчетов в столбец комплексных чисел
                    stc = st[::2] + 1j * st[1::2]
                    # добавление нулей в конец массива 
                    stc = np.concatenate((stc, np.zeros(self.power_two - len(stc), dtype=np.complex128)))  # Добавление нулевых элементов

                    if self.impactChPK:
                        # если установлена ЧКП
                        for j in range(len(self.RGG_ChKP)):
                            if self.coord_ChKP[j][0]-self.coord_ChKP[j][1]/2< i+1<= self.coord_ChKP[j][0]+self.coord_ChKP[j][1]/2:
                                # добавление в столбцы исходной РГГ столбцов РГГ ЧКП 
                                stc += self.RGG_ChKP[j][:, self.ChKP_column_count[j]]
                                self.ChKP_column_count[j] += 1
                                        
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
                pass
                # for i in range(X0):
                #     stc = Rgg_ChKP2[:, i]
                #     sp_stc = np.fft.fft(stc.T)
                #     svRG = sp_stc* sp_OF  # Умножение спектров столбца на опорную функцию
                #     svRG = np.fft.ifft(svRG)
                #     write_frame = np.concatenate((np.real(svRG), np.imag(svRG)))
                #     write_frame.astype(np.float32).tofile(rpg_file)  # Запись в файл
                    
            print(f'РГГ свернута по дальности, время: {np.round(time.time()-self.start_time, 2)} c.')

    def hamming_averaging(self, RLI, px:float, permission_x:float, permission_y:float, is_rescaling: bool = True)-> np.ndarray:
        """Усреднения Хэмминга
        Если is_rescaling=1 - выполняем перемасштабирование РЛИ к квадратному значению размером px
        Если is_rescaling=0 - просто выполняем осреднение без изменения размера значения
        """
        new_RLI = np.fft.fft2(RLI)
        RLI = None
        Ndf0, Naf0 = new_RLI.shape

        if is_rescaling:
            Coef_1_r = px / self.dnr  # Коэффициент переквантования РГГ по дальности
            Coef_1_x = px / self.dx  # Коэффициент переквантования РГГ по азимуту

            if Coef_1_x < 1:
                raise ValueError('Необходима раздвижка спектра по азимуту')

        
            # Масштабирование РЛИ по координате дальности
            if Coef_1_r < 1:
                # Выполняем раздвижку спектра по дальности
                Ndrz2 = int(np.fix(Ndf0 / Coef_1_r / 2) * 2)
                Nd_zeros = np.zeros((Ndrz2 - Ndf0, Naf0))
                new_RLI = np.vstack((new_RLI[:Ndf0//2, :], Nd_zeros, new_RLI[Ndf0//2:, :]))
        
            if Coef_1_r > 1:
                # Удаляем избыточные отсчеты в спектре по дальности
                Nr1 = int(np.fix(Ndf0 / Coef_1_r / 4) * 2)
                new_RLI = new_RLI[Nr1:Ndf0 - Nr1, :]
        
            # Масштабирование РЛИ по координате азимута
            if Coef_1_x > 1:
                # Удаляем избыточные отсчеты в спектре по азимуту
                Nx1 = int(np.fix(Naf0 / Coef_1_x / 4) * 2)
                new_RLI = np.delete(new_RLI, np.s_[Nx1:Naf0-Nx1], axis=1)
        
            dx2 = px
            dnr2 = px
    
        else:
            dx2 = self.dx
            dnr2 = self.dnr
        '------------------Конец процедуры масштабирования------------------'
        # Осреднение РЛИ
        Ndf,Naf = new_RLI.shape
        Coef_2_r = (permission_y / dnr2)/2  # Коэффициент осреднения РЛИ по дальности
        Coef_2_x = (permission_x / dx2)/2  # Коэффициент осреднения РЛИ по азимуту
        
        # Оптимизированная аподизация Хэмминга
        Kh = 0.08
        Nh = 2
        Nr1 = int(np.fix(Ndf / Coef_2_r / 4) * 2) # c extnjv pfuhe,ktybz
        Nx1 = int(np.fix(Naf / Coef_2_x / 4) * 2)
        
        # Формирование модулирующих функций
        # по x
        MF_Hem_x = np.zeros(Naf)  
        MF_Hem_x[0] = 1
        _i = np.arange(1, Nx1)
        _MF_x = Kh + (1 - Kh) * np.cos(np.pi * (_i+1) / Nx1 / 2) ** Nh
        # заполнение начальных индексов
        MF_Hem_x[1:Nx1] = _MF_x
        # заполнение конечных индексов
        MF_Hem_x[Naf-Nx1+1:] =  _MF_x[::-1]

        # по y
        MF_Hem_y= np.zeros(Ndf)  
        _i = np.arange(1, Nr1)
        _MF_y = Kh + (1 - Kh) * np.cos(np.pi * (_i+1) / Nr1 / 2) ** Nh
        # заполнение начальных индексов
        MF_Hem_y[1:Nr1] = _MF_y
        # заполнение конечных индексов
        MF_Hem_y[Ndf-Nr1+1:] =  _MF_y[::-1]
    
        # Аподизация по строкам
        I_Hem = new_RLI * MF_Hem_x
    
        # Аподизация по столбцам
        I_Hem2 = I_Hem * MF_Hem_y[:, np.newaxis]
    
        # Обратное преобразование Фурье
        CRLIsr = np.fft.ifft2(I_Hem2)
    
        return CRLIsr




    class ChKP_builder():
        def __init__(self, ChKPs_param: list, parent) -> None:
            """Класс принимает параметры:
            ChKP_param: [[]]
                ChKP_location_x - координата x ЧКП внутри исходной РГГ [отсчеты];
                ChKP_location_y - координата у ЧКП внутри исходной РГГ [отсчеты].
                Chkp_power - мощность ЧПК [без размера];
                ChKP_size_r - размер ЧКП по наклонной дальности;
                ChKP_size_x - размер ЧКП по азимуту;
         
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

            for i in range(len(ChKPs_param)):
                coord_ChKP, RGG_ChKP = self.get_ChKP_RGG(ChKPs_param[i])
                self.RSA_param.coord_ChKP.append(coord_ChKP)
                self.RSA_param.RGG_ChKP.append(RGG_ChKP)
                
                print(f'Сформирована {i+1}-я ЧКП, время: {np.round(time.time()-self.RSA_param.start_time, 2)} c.')
   
        def get_ChKP_RGG(self, ChKP_param):
            """Метод производит синтезировать РГГ ЧКП"""           
           
            # распаковка параметров ЧКП
            ChKP_location_x, ChKP_location_y, Chkp_power, ChKP_size_r, ChKP_size_x,   = ChKP_param
            N_razb_r = ChKP_size_r/self.RSA_param.resolution_r  # количество разбиений РГГ по дальности
            N_razb_x = ChKP_size_x/self.RSA_param.resolution_x # количество разбиений РГГ по азимуту
            Nd_r = int(np.ceil(self.N1/N_razb_r)) # количество когерентных отсчетов на одном участке разбиения по дальности    
            Nd_x = int(np.ceil(self.RSA_param.Nas/N_razb_x)) # количество когерентных отсчетов на одном участке разбиения по азимуту
            Fakt_razb_r = int(np.ceil(self.N1/Nd_r)) # Fakt_razb_r может отличаться от N_razb_r на +- 1
            Fakt_razb_x = int(np.ceil(self.RSA_param.QR/Nd_x)) # Для самолета Nas<<QR, следовательно Nd_x<<Fakt_razb_x
            Mdop=0
            
            # формирование случайной функции ЧКП
            s = random.randint(1,40)
            np.random.seed(s) # установка начального генератора случайной величины
            U = (np.random.rand(Fakt_razb_r, Fakt_razb_x) - 0.5) * 2 * np.pi

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
            phase = self.RSA_param.LCHM + self.w * rt
            ndop = ((rt - self.RSA_param.R) // self.RSA_param.dnr).astype(int)
            Imp0 = np.sin(phase) + 1j * np.cos(phase)

            # Вычисление значений массива ndop и заполнение массивов Imp и U_sl
            for i in range(self.RSA_param.QR):
                U_sl = np.zeros((Nd_ChKP,1), dtype=complex)
                Imp = np.zeros((Nd_ChKP,1), dtype=complex)
                z = Imp0[:,i].reshape((-1,1))
                Imp[ndop[i] + Mdop:ndop[i] + Mdop + self.N1] = z
                qq = i // Nd_x
                U_sl[ndop[i] + Mdop:ndop[i] + Mdop + self.N1,0] = U_sl0_compl[:, qq]
                # Заполнение Rgg_ChKP значением Imp * U_sl
                Rgg_ChKP[:, i] = (Imp * U_sl).ravel()

            Rgg_ChKP *= Chkp_power
            # Получение размеров Y0 и X0 массива Rgg_ChKP
            Y0, X0 = Rgg_ChKP.shape
        
            Rgg_ChKP2 = np.zeros((self.RSA_param.power_two, X0), dtype=np.complex128)
            Rgg_ChKP2[ChKP_location_y:Y0 + ChKP_location_y, :] = Rgg_ChKP

            coord_ChKP = (ChKP_location_x, X0)

            return coord_ChKP, Rgg_ChKP2

    
    def save_prj_json(self):
        # формирование словаря ЧКП
        data_ChKP = {}
        for i in range(len(self.ChKP_param)):                
            data_ChKP[f'{i+1}'] = {'Размер ЧКП по дальности': self.ChKP_param[i][0],
                                   'Размер ЧКП по азимуту': self.ChKP_param[i][1],
                                   'Мощность ЧПК': self.ChKP_param[i][2],
                                   'Координата ЧКП по оси x': self.ChKP_param[i][3],
                                    'Координата ЧКП по оси y': self.ChKP_param[i][4],
                                   }


        data = {
                'Дата синтезирования': f'{datetime.datetime.now()}',
                'РСА': '-',
                'Параметры РСА': {
                                   'Количество комплексных отсчетов': self.Ndn, 
                                   'Количество зарегистрированных импульсов': self.Na,
                                   'Частота дискретизации АЦП':    self.fcvant,
                                   'Длина волны':   self.lamb, 
                                   'Период повторения импульсов':  self.Tpi,
                                   'Ширина спектра сигнала': self.Fsp,
                                   'Длительность импульса':    self.Dimp, 
                                   'Скорость движения носителя':   self.movement_speed,
                                   'Размер антенны по азимуту':  self.AntX,
                                   'Наклонная дальность': self.R,
                                },
                'Путь до файла *.rpt': self.path_output_rpt,
                'Количество добавленных ЧКП': len(self.ChKP_param),
                'Параметры ЧКП': data_ChKP,
                'Другие параметры': 'Другие параметры',
                }

        # Открытие файла для записи
        with open(f'{self.file_path[:-4]}.json', 'w', encoding='utf-8') as file:
            # Запись данных в файл в формате JSON
            json.dump(data, file, ensure_ascii=False)
      

if __name__ == '__main__':

    param_RSA = [10944+64, 165500, 400e6, 0.0351, 485.692e-6, 300e6, 10e-6, 108, 0.23, 4180]
    ChKP = [[8400, 3190, 25, 100, 450]]


    sf = Convolution(param_RSA, "C:/Users/X/Desktop/185900/1.rgg", ChKP_param=ChKP, auto_px_norm='hemming')

    sf.range_convolution_ChKP()
    sf.azimuth_convolution_ChKP(ROI=[0,2000,20000,2000])
    # sf.azimuth_convolution_ChKP()
    
   
