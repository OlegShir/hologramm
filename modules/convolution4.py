
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
from progress.bar import IncrementalBar
from PIL import Image, ImageOps
from modules.file_manager import project_json_writer
from modules.ChKP_builder import ChKPBuider
import time
from halo import Halo


class Convolution():
    def __init__(self,
                 RSA_param:list, #
                 file_path: str, # путь до файла РГГ
                 file_name: str, # название файла РГГ (опционально)
                 full_RGG:bool = True, # тип обработки - если True, то обрабатывается вся РРГ, иначе только ЧКП
                 ChKP_param: list =[int] , # список параметров ЧКП вида []
                 auto_px_norm: str = 'auto', # режим нормализации пикселей РЛИ
                 file_path_project: str = '',
                 ) -> None:
        print("Инициализация данных")
        self.ChKP_param = ChKP_param     
        self.full_RGG = full_RGG
        self.file_path:str = file_path # путь до файла РГГ
        self.file_name:str = file_name # название файла РГГ (опционально)  # получение пути для сохранения
        self.auto_px_norm = auto_px_norm
        self.file_path_project = file_path_project
        # для ЧПК они повторяются 
        self.N_otst = 0 # количество импульсов пропускаемых при чтении РГГ
        # self.Na = 90000
        # распаковка параметров РСА
        self.get_init_param_RSA(RSA_param)
        self.impactChPK = False
        # настройка отображения процесса выполнения свертки
        self.suffix = '%(percent)d%% [%(elapsed_td)s / %(eta_td)s]'

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
            self.ChKP = ChKPBuider(self.ChKP_param, self)
        else:
            self.impactChPK = False 
        self.path_output_rpt:str = self.get_path_output_rpt()

    def get_init_param_RSA(self, RSA_param:list) -> None:
        """
        Инициализирует распаковку параметров РСА, принимаемых списком из хранилища.
        """
        Ndn, Nazim, fcvant, lamb, Tpi, Fsp, Dimp, movement_speed, AntX, R, coef_resize= RSA_param

        self.Ndn:int = Ndn # количество комплексных отсчетов
        self.Na:int = Nazim # количество зарегистрированных импульсов
        self.fcvant:int = fcvant # частота дискретизации АЦП
        self.lamb:float = lamb # длина волны
        self.Tpi:float = Tpi # период повторения импульсов
        self.Fsp:int = Fsp # ширина спектра сигнала
        self.Dimp:float = Dimp # длительность импульса
        self.movement_speed:float = movement_speed # скорость движения носителя
        self.AntX:float = AntX # размер антенны по азимуту
        self.R:int = R # наклонная дальность (до объекта прикрытия)
        self.coef_resize:float = coef_resize # коэффициент сжатия РГГ при формировании изображения

    def get_path_output_rpt(self) -> str:
        if self.full_RGG:
            # создание имени файла в зависимости от необходимой свертки
            if self.impactChPK:
                # фаил с результатами свертки по дальности суммарной РГГ (РГГ + ЧКП)
                output_file_path = f"{self.file_path}/{self.file_name}_with_{len(self.ChKP_param)}ChKP.rpt"
            else:
                # фаил с результатами свертки по дальности только исходной РГГ 
                output_file_path = f"{self.file_path}/{self.file_name}.rpt"
        else:
            # фаил с результатами свертки по дальности только ЧКП
            output_file_path = f"{self.file_path}/{self.file_name}_only_ChKP.rpt"
        
        return output_file_path
    

    def range_convolution_ChKP(self) -> None:
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
        with open(f"{self.file_path}/{self.file_name}.rgg", 'rb') as rgg_file, open(self.path_output_rpt, 'wb') as rpg_file:
            # установка начала считывания голограммы
            rgg_file.seek(2*self.Ndn*self.N_otst, 0)          
            
            if self.full_RGG:
                for i in IncrementalBar("Свертка исходной РГГ по дальности", suffix = self.suffix).iter(range(self.Na)):
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
          
    
    def azimuth_convolution_ChKP(self, 
                                 ROI:list = [], # область РГГ, которая будет сворачиваться по азимуту в РЛИ
                                 path_input_rpt:str = ''
                                ):
        """------------------------ROI--------------------
                     ---->|N_otst_r
                |   +-----|------------------------------+
                |   |.....|..............................|
                v___|_____|____Na_____...................|
            N_otst_y|.....|///////////|..................|
                    |.....|///////////|Ndrz..............|
                    |.....|///////////|..................|
                    |....................................|
                    +------------------------------------+
        ROI = [N_otst_r, N_otst_y, Na, Ndrz]
        """
        if ROI:
            # если область задана, то производится распаковка параметров
            N_otst_r, N_otst_y, Na, Ndrz  = ROI
        else:
            # если область не задана, то она равна всей РГГ
            N_otst_r = N_otst_y = 0
            Na = self.Na
            Ndrz = self.Ndn
       
        self.N_otst_y = N_otst_y
        self.Ndrz = Ndrz

        if not path_input_rpt:
            # если путь не введен, то по умолчанию используется путь сохраненный при сворачивании по дальности
            path_input_rpt = self.path_output_rpt
        # предварительное выделение памяти для массива свертки РГГ
        rgg1 = np.empty((Ndrz, Na), dtype=np.complex128)

        with open(path_input_rpt, 'rb') as fid1:
            fid1.seek(2 * self.power_two * N_otst_r * 4 + N_otst_y * 4)
            for i in IncrementalBar("Подготовка данных                ", suffix = self.suffix).iter(range(Na)):
                r1 = np.fromfile(fid1, dtype=np.float32, count=Ndrz)
                fid1.seek((self.power_two - Ndrz) * 4, 1)
                r2 = np.fromfile(fid1, dtype=np.float32, count=Ndrz)
                fid1.seek((self.power_two - Ndrz) * 4, 1)
                rgg1[:, i] = r1 + 1j * r2
       
        # Высота блока в отсчетах (по изображению)
        Ndr = 2
        # определение начальной наклонной дальности на выбранной ROI
        R_start = self.R + (N_otst_y- Ndr / 2)*self.dnr
        # Количество разбиений (блоков) по наклонной дальности
        Nbl_r = np.round(Ndrz / Ndr).astype(int)
        # инициализация переменных для цикла
        Las_bl = np.zeros(Nbl_r)
        RLI1 = np.empty((Ndrz, Na), dtype=np.complex128)
        # ----------------------------------
                              
        for i in IncrementalBar("Свертка исходной РГГ по азимуту  ", suffix = self.suffix).iter(range(Nbl_r)):
                 
            # Наклонная дальность до центра блока в метрах
            R_centr_bl = R_start + ((i+1) * Ndr) * self.dnr  

            Nas_bl = int((self.lamb * R_centr_bl) // (2 * self.resolution_x * self.dx))

            Las_bl = Nas_bl * self.dx 
            x_max = Las_bl / 2 * self.dx
            rt1_max_bl = np.sqrt(R_centr_bl ** 2 + x_max ** 2) - R_centr_bl
            dop_Ndr = int(np.round(rt1_max_bl / self.dnr))
 
            if dop_Ndr > Ndrz - (i+1) * Ndr:
                dop_Ndr = Ndrz - (i+1) * Ndr
            elif dop_Ndr < 0:
                raise ValueError("Величина dop_Ndr не может быть меньше нуля")

            Ndr_bl = Ndr + dop_Ndr
            OF2_bl = np.zeros((Ndr_bl, Nas_bl), dtype=np.complex128)

            x = np.arange(-Nas_bl / 2, Nas_bl / 2) * self.dx
            rt = np.sqrt(R_centr_bl ** 2 + x ** 2)
            phase = -4 * np.pi * rt / self.lamb
            OF1_bl = np.cos(phase) + 1j * np.sin(phase)
            OF2_bl[:Ndr_bl, np.arange(Nas_bl)] = OF1_bl
            OF_bl = np.zeros((Ndr_bl, Na), dtype=np.complex128)

            if Na / 2 < Nas_bl / 2:
                raise ValueError("Не выполняется условие Na/2 >= Nas_bl/2 + dsm")

            OF_bl[:, int(Na / 2 - Nas_bl / 2):int(Na / 2 + Nas_bl / 2)] = OF2_bl
            sp_OF_bl = np.fft.fft2(OF_bl)
            rgg1_bl = rgg1[i * Ndr:(i+1) * Ndr + dop_Ndr, :]
            sp_rgg1_bl = np.fft.fft2(rgg1_bl)
            RLI1_bl = sp_rgg1_bl * np.conj(sp_OF_bl)
            RLI1_bl = np.abs(np.fft.ifft2(RLI1_bl))
            RLI1[i * Ndr:(i+1) * Ndr, :] = RLI1_bl[:Ndr, :]
                  
        # АРЛИ суммарной РГГ
        RLI1 = np.fft.fftshift(RLI1, axes=1)
        # сохранение файла описания
        project_json_writer(self)
        # сохранение изображения
        self.save_RLI_PIL(RLI1)
    
    def save_RLI_PIL(self, RLI:np.ndarray) -> None:
        with Halo(text='Формирование РЛИ                  ', spinner="dots2",  placement='right', color="white", ):
        
            # Вычисление амплитуды (модуля) 
            amplitude_values = np.power(np.abs(RLI), 0.3)
            # Линейная нормализация значений         
            normalized_values = (amplitude_values - np.min(amplitude_values)) / (np.max(amplitude_values) - np.min(amplitude_values))
            # Преобразование в диапазон от 0 до 255
            scaled_data = (normalized_values * 255).astype(np.uint8)

            # Создание объекта изображения с градациями серого
            image = Image.fromarray(scaled_data, mode='L')

            # Масштабирование изображение в соответствии с параметрами dnr и dx
            factor_r = 0.25 / self.dnr  # Коэффициент переквантования РГГ по дальности
            factor_x = 0.25 / self.dx  # Коэффициент переквантования РГГ по азимуту
            image = image.resize((int(image.width*factor_r*0.1), int(image.height*factor_x*0.1)), Image.HAMMING)  
            # Сохранение изображения
            image.save(f"{self.file_path}/{self.file_name}.png",  optimize=True, quality=95)
        
        print("РЛИ сформировано")     

if __name__ == '__main__':


    param_RSA = [10944+64, 165562, 400e6, 0.0351, 485.692e-6, 300e6, 10e-6, 108, 0.23, 2250, 0.1]
    #ChKP = [[8400, 5000, 25, 100, 450]]
    ChKP=[]


    sf = Convolution(param_RSA, "F:/RGG source/185900", "1", ChKP_param=ChKP, auto_px_norm='none')

    sf.range_convolution_ChKP()
    sf.azimuth_convolution_ChKP()

    # sf.azimuth_convolution_ChKP(ROI=[0, 2000, 20000, 2000], path_input_rpt="C:/Users/X/Desktop/185900/1_with_1ChKP.rpt")
    
   
