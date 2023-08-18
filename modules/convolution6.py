
"""Модуль производит свертку РГГ.
        Аргументы:
        - параметры РСА:
                        [количество комплексных отсчетов, количество зарегистрированных импульсов, частота дискретизации АЦП, длина волны,...
                        период повторения импульсов, ширина спектра сигнала, длительность импульса, скорость движения носителя,...
                        размер антенны по азимуту, минимальная наклонная дальность (до объекта прикрытия), коэффициент сжатия,
                        минимальное значения РГГ, максимальное значение РГГ, среднее значение фона, значение фона в дБ ]
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
#import psutil
import os
import numpy as np
from progress.bar import IncrementalBar
from PIL import Image
from modules.file_manager import project_json_writer
from modules.ChKP_builder import ChKPBuider
from halo import Halo
from os import remove


class Convolution():
    def __init__(self,
                 RSA_param: dict, #
                 file_path: str, # путь до файла РГГ
                 file_name: str, # название файла РГГ (опционально)
                 RSA_name:str, # название РСА
                 ChKP_param: list = [] , # список параметров ЧКП вида []
                 file_path_project: str = '',
                 ROI:list = [], # область РГГ, которая будет сворачиваться по азимуту в РЛИ
                 accuracy = 64,
                 fon: bool = False, # Определяет, что происходит вычисление среднего значения фона
                 save_ROI_to_np:bool = False, # Сохранение свертки РОИ в фаил np
                 count_fon= '',
                
                 ) -> None:
        self.RSA_param = RSA_param
        self.ChKP_param = ChKP_param     
        self.RSA_name = RSA_name
        self.file_path:str = file_path # путь до файла РГГ
        self.file_name:str = file_name # название файла РГГ (опционально)  # получение пути для сохранения
        self.file_path_project = file_path_project
        self.fon = fon
        self.save_ROI_to_np = save_ROI_to_np
        self.ROI = ROI
        # распаковка параметров РСА
        self.get_init_param_RSA(RSA_param)
        self.count_fon = count_fon #!
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
        if self.ROI:
            # если область задана, то производится распаковка параметров
            self.N_otst_r, self.N_otst_y, self.Na, self.Ndrz  = ROI
        else:
            # если область не задана, то она равна всей РГГ
            self.N_otst_r = self.N_otst_y = 0
            self.Na = self.Na
            self.Ndrz = self.Ndn
      
        self.impactChPK = False
        self.accuracy_int = accuracy
        self.accuracy = np.complex128 if self.accuracy_int == 128 else np.complex64

        # выбор начального заголовка
        if self.fon:
            title = "Расчет значения фона"
            if self.ChKP_param:
                title = "Расчет значения ЧКП"
        else:
            title = "Инициализация данных"
        print(title)
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
        if self.fon:
            self.length_check_Na()

    def length_check_Na(self) -> None:
        """Метод проверяет длину Na на соответствие условию Na/2 >= Nas_bl/2"""
        self.Na_dop = 0
        # определение начальной наклонной дальности на выбранной ROI
        R_start = self.R + (self.N_otst_y - 1)*self.dnr
        # максимальное разбиение (блоков) по наклонной дальности
        max_R_centr_bl = R_start + int((self.Ndrz//2)*2) * self.dnr
        self.max_Nas_bl = int((self.lamb * max_R_centr_bl) // (2 * self.resolution_x * self.dx))
        if self.Na < self.max_Nas_bl:
            # если условие не выполняется
            self.Na_dop = self.max_Nas_bl//self.Na + 1
            # увеличиваем ширину Na
            self.Na *= self.Na_dop


    def get_init_param_RSA(self, RSA_param:dict) -> None:
        """
        Инициализирует распаковку параметров РСА, принимаемых списком из хранилища.
        """
        self.Ndn:int = RSA_param.get("Количество комплексных отсчетов", 0) # количество комплексных отсчетов
        self.Na:int = RSA_param.get("Количество зарегистрированных импульсов", 0) # количество зарегистрированных импульсов
        self.fcvant:int = RSA_param.get("Частота дискретизации АЦП", 0) # частота дискретизации АЦП
        self.lamb:float = RSA_param.get("Длина волны", 0) # длина волны
        self.Tpi:float = RSA_param.get("Период повторения импульсов", 0) # период повторения импульсов
        self.Fsp:int = RSA_param.get("Ширина спектра сигнала", 0) # ширина спектра сигнала
        self.Dimp:float = RSA_param.get("Длительность импульса", 0) # длительность импульса
        self.movement_speed:float = RSA_param.get("Скорость движения носителя", 0) # скорость движения носителя
        self.AntX:float = RSA_param.get("Размер антенны по азимуту", 0) # размер антенны по азимуту
        self.R:int = RSA_param.get("Минимальная наклонная дальность", 0) # минимальная наклонная дальность

        self.coef_resize:float = RSA_param.get("Коэффициент сжатия", 0) # коэффициент сжатия РГГ при формировании изображения
        self.min_value_px = RSA_param.get("Минимальное значение РЛИ", 0) # Минимальное значение пикселя в матрице РЛИ
        self.max_value_px = RSA_param.get("Максимальное значение РЛИ", 0) # Максимальное значение пикселя в матрице РЛИ
        self.quantiles = RSA_param.get("Значение квантиля", 0)

    def get_path_output_rpt(self) -> str:

        # создание имени файла в зависимости от необходимой свертки
        if self.impactChPK:
            # фаил с результатами свертки по дальности суммарной РГГ (РГГ + ЧКП)
            output_file_path = f"{self.file_path}/{self.file_name}_with_{len(self.ChKP_param)}ChKP.rpt"
        else:
            # фаил с результатами свертки по дальности только исходной РГГ 
            output_file_path = f"{self.file_path}/{self.file_name}.rpt"
        
        return output_file_path

    def range_convolution_ChKP(self, Na_full_rgg = 0, N_ots_full_rgg = 0) -> None:
        if Na_full_rgg:
            self.Na = Na_full_rgg
            self.N_otst_r = N_ots_full_rgg
        # ====== Формирование ОФ для свертки зондирующего импульса ============
        N2 = self.N1 // 2
        opor_func_1 = np.zeros((self.power_two, 1), dtype=self.accuracy)
        opor_func_1[:self.N1] = np.cos(self.LCHM) + 1j * np.sin(self.LCHM) # фаза сигнала в комплексном виде
        opor_func_2 = np.zeros((self.power_two, 1), dtype=self.accuracy)
        opor_func_2[:N2] = opor_func_1[N2:self.N1]                
        opor_func_2[self.power_two-N2:self.power_two] = opor_func_1[:N2]
        # ftt работает только со строкой, поэтому производится транспонирование
        sp_OF = np.fft.fft(opor_func_2.T)
        svRG = np.zeros((self.power_two,1), dtype=self.accuracy)  # Инициализация массива размером Nd с нулями
        # открытие файла голограммы и файла для записи свертки по дальности
        with open(f"{self.file_path}/{self.file_name}.rgg", 'rb') as rgg_file, open(self.path_output_rpt, 'wb') as rpg_file:
            # установка начала считывания голограммы
            rgg_file.seek(2*self.Ndn*self.N_otst_r, 0)          

            for i in IncrementalBar("Свертка исходной РГГ по дальности", suffix = self.suffix).iter(range(self.Na)):
                # значение считываются в диапазоне от -127 до +128
                st = np.fromfile(rgg_file, dtype=np.int8, count=self.Ndn*2) 
                # заполнение первых 128 значений нулем
                st[:128] = 0                    
                # Преобразование удвоенного количества отсчетов в столбец комплексных чисел
                stc = st[::2] + 1j * st[1::2]
                # добавление нулей в конец массива 
                stc = np.concatenate((stc, np.zeros(self.power_two - len(stc), dtype=self.accuracy)))  # Добавление нулевых элементов

                if self.impactChPK:
                    # если установлена ЧКП
                    for j in range(len(self.RGG_ChKP)):
                        if self.coord_ChKP[j][0]-self.coord_ChKP[j][1]/2< i+self.N_otst_r+1<= self.coord_ChKP[j][0]+self.coord_ChKP[j][1]/2:
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
                                 path_input_rpt:str = '',
                                 full_RGG = False, # если свертку производить частями
                                 ):
        
        if not path_input_rpt:
            # если путь не введен, то по умолчанию используется путь сохраненный при сворачивании по дальности
            path_input_rpt = self.path_output_rpt
        # предварительное выделение памяти для массива свертки РГГ
        rgg1 = np.empty((self.Ndrz, self.Na), dtype=self.accuracy)

        with open(path_input_rpt, 'rb') as fid1:
            fid1.seek(2 * self.power_two * 0 + self.N_otst_y * 4)
            for i in IncrementalBar("Подготовка данных                ", suffix = self.suffix).iter(range(self.Na)):
                r1 = np.fromfile(fid1, dtype=np.float32, count=self.Ndrz)
                fid1.seek((self.power_two - self.Ndrz) * 4, 1)
                r2 = np.fromfile(fid1, dtype=np.float32, count=self.Ndrz)
                fid1.seek((self.power_two - self.Ndrz) * 4, 1)
                rgg1[:, i] = r1 + 1j * r2
       
        # Высота блока в отсчетах (по изображению)
        Ndr = 2
        # определение начальной наклонной дальности на выбранной ROI
        R_start = self.R + (self.N_otst_y - Ndr / 2)*self.dnr
        # Количество разбиений (блоков) по наклонной дальности
        Nbl_r = np.round(self.Ndrz / Ndr).astype(int)
        # инициализация переменных для цикла
        Las_bl = np.zeros(Nbl_r)

        # Попытка создать массив, который может вызвать MemoryError
        try:
            RLI1: np.ndarray = np.empty((self.Ndrz, self.Na), dtype=self.accuracy) # type: ignore
        except MemoryError:
            if os.path.exists(self.path_output_rpt):
                remove(self.path_output_rpt)
            raise # Передача исключения обратно
        # ----------------------------------                      
        for i in IncrementalBar("Свертка исходной РГГ по азимуту  ", suffix = self.suffix).iter(range(Nbl_r)):
            # Наклонная дальность до центра блока в метрах
            R_centr_bl = R_start + ((i+1) * Ndr) * self.dnr  

            Nas_bl = int((self.lamb * R_centr_bl) // (2 * self.resolution_x * self.dx))
            Las_bl = Nas_bl * self.dx 
            x_max = Las_bl / 2 * self.dx
            rt1_max_bl = np.sqrt(R_centr_bl ** 2 + x_max ** 2) - R_centr_bl
            dop_Ndr = int(np.round(rt1_max_bl / self.dnr))
 
            if dop_Ndr > self.Ndrz - (i+1) * Ndr:
                dop_Ndr = self.Ndrz - (i+1) * Ndr
            elif dop_Ndr < 0:
                raise ValueError("Величина dop_Ndr не может быть меньше нуля")

            Ndr_bl = Ndr + dop_Ndr
            OF2_bl = np.zeros((Ndr_bl, Nas_bl), dtype=self.accuracy)

            x = np.arange(-Nas_bl / 2, Nas_bl / 2) * self.dx
            rt = np.sqrt(R_centr_bl ** 2 + x ** 2)
            phase = -4 * np.pi * rt / self.lamb
            OF1_bl = np.cos(phase) + 1j * np.sin(phase)
            OF2_bl[:Ndr_bl, np.arange(Nas_bl)] = OF1_bl
            OF_bl = np.zeros((Ndr_bl, self.Na), dtype=self.accuracy)

            OF_bl[:, int(self.Na / 2 - Nas_bl / 2):int(self.Na / 2 + Nas_bl / 2)] = OF2_bl
            sp_OF_bl = np.fft.fft2(OF_bl)
            rgg1_bl = rgg1[i * Ndr:(i+1) * Ndr + dop_Ndr, :]
            sp_rgg1_bl = np.fft.fft2(rgg1_bl)
            RLI1_bl = sp_rgg1_bl * np.conj(sp_OF_bl)
            RLI1_bl = np.abs(np.fft.ifft2(RLI1_bl))
            RLI1[i * Ndr:(i+1) * Ndr, :] = RLI1_bl[:Ndr, :]
        
        with Halo(text='Подготовка данных', spinner="dots2",  placement='right', color="white", ):
            # АРЛИ суммарной РГГ
            RLI1 = np.fft.fftshift(RLI1, axes=1)
        with Halo(text='Удаление временных файлов', spinner="dots2",  placement='right', color="white", ):
            remove(self.path_output_rpt)

        # Вычисление амплитуды (модуля) 
        amplitude_values = np.abs(RLI1)
        # получение среднего значения яркости РОИ
        if self.fon:
           # тут учитывается условие Na/2 >= Nas_bl/2
           if self.Na_dop:
               amplitude_values = amplitude_values[:, :amplitude_values.shape[1]//self.Na_dop]
           ave_ROI = np.mean(amplitude_values).astype(float)
        #    self.save_RLI_PIL(amplitude_values, self.count_fon)
           return ave_ROI
        if full_RGG:
            return amplitude_values
        if self.save_ROI_to_np:
            np.save(f"{self.file_path}/{self.file_name}_ROI", amplitude_values)
        # сохранение изображения
        self.save_RLI_PIL(amplitude_values)
    
    def full_RGG_part(self) -> None:
        # размер в байтах одного столбца
        # need_memory = self.Na*self.Ndn *8

        # memory = psutil.virtual_memory()
        # memory.available

        
        part = self.Na//(5*self.max_Nas_bl)
        # вычисляем количество частей 
        whole_part = self.Na // part
        remainder = 0
        print('В целях оптимизации процесса производится свертка частями')
        for i in range(part):
            print(f'{i+1}/{part}')
            if i == part-1:
                remainder = self.Na % part
            self.range_convolution_ChKP(Na_full_rgg = whole_part + remainder,  N_ots_full_rgg = i*whole_part)
            np_array:np.ndarray = self.azimuth_convolution_ChKP(full_RGG=True) # type: ignore
            np.save(f"{self.file_path}/np_{i}", np_array)
        # Создание пустого массива, куда будем объединять данные
        merged_array = np.empty((self.Ndrz, 0), dtype=np.float32)
        for i in range(part):  # Предполагается, что  файлы названы от "*.npy"
            file_path = f"{self.file_path}/np_{i}.npy"
            loaded_array = np.load(file_path)
            merged_array = np.concatenate((merged_array, loaded_array), axis=1)
            remove(file_path)
        
        self.save_RLI_PIL(merged_array)       


    def save_RLI_PIL(self, amplitude_values:np.ndarray, count = '') -> None:
        with Halo(text='Формирование РЛИ', spinner="dots2",  placement='right', color="white", ):

            # Отсортируем массив
            sorted_values = np.sort(amplitude_values)

            # Случай когда изображение формируется впервые
            if not self.quantiles:
                self.min_value_px = np.min(amplitude_values)
                self.RSA_param["Минимальное значение РЛИ"] = int(self.min_value_px) # type: ignore
                self.max_value_px = np.max(amplitude_values)
                self.RSA_param["Максимальное значение РЛИ"] = int(self.max_value_px) # type: ignore
                # Найдем квантиль 97% (0.97) массива
                self.quantiles = np.quantile(sorted_values, 0.97) # type: ignore
                self.RSA_param["Значение квантиля"] = self.quantiles
            
            # Вычислим диапазон значений, попадающих в исходный диапазон [2 * quantiles, max_value_px]
            values_in_original_range = sorted_values[(sorted_values >= 2 * self.quantiles) & (sorted_values <= self.max_value_px)] # type: ignore

            # Приведем этот диапазон к диапазону quantiles
            new_range_min = self.quantiles
            new_range_max = 2 * self.quantiles

            # Масштабируем значения из исходного диапазона к новому диапазону
            scaled_values = ((values_in_original_range - (2 * self.quantiles)) / (self.max_value_px - (2 * self.quantiles))) * (new_range_max - new_range_min) + new_range_min # type: ignore

            # Обновим значения в массиве
            amplitude_values[(amplitude_values >= 2 * self.quantiles) & (amplitude_values <= self.max_value_px)] = scaled_values

            # Линейная нормализация значений                     
            normalized_values = (amplitude_values - self.min_value_px) / (2*self.quantiles - self.min_value_px) # type: ignore
            # Преобразование в диапазон от 0 до 255
            scaled_data = (normalized_values * 255).astype(np.uint8)

            # Создание объекта изображения с градациями серого
            image = Image.fromarray(scaled_data, mode='L')

            # Масштабирование изображение в соответствии с параметрами dnr и dx
            factor_r = 0.25 / self.dnr  # Коэффициент переквантования РГГ по дальности
            factor_x = 0.25 / self.dx  # Коэффициент переквантования РГГ по азимуту
            image = image.resize((int(image.width*factor_r*self.coef_resize), int(image.height*factor_x*self.coef_resize)), Image.HAMMING) 
            if not self.ROI:
                image.save(f"{self.file_path}/{self.file_name}.png")
            else:
                # Сохранение изображения
                image.save(f"{self.file_path}/{self.file_name}_ROI{count}.png")
        
            print("РЛИ сформировано")


if __name__ == '__main__':


    param_RSA = {
        "Количество комплексных отсчетов": 2000,
        "Количество зарегистрированных импульсов": 4000,
        "Частота дискретизации АЦП": 400e6,
        "Длина волны": 0.0351,
        "Период повторения импульсов": 485.692e-6,
        "Ширина спектра сигнала": 300e6,
        "Длительность импульса": 10e-6,
        "Скорость движения носителя": 108,
        "Размер антенны по азимуту": 0.23,
        "Минимальная наклонная дальность": 2250,
        "Коэффициент сжатия": 0.3,
        "Минимальное значение РЛИ": 0,
        "Максимальное значение РЛИ": 0,
        "Значение квантиля": 0,
        "Коэффициент сигнал/фон": 6.53,
        "Значение фона в дБ": -12
        }
    
        #     "Минимальное значение РЛИ": 8  0.9324899,
        # "Максимальное значение РЛИ": 19659743  50922690.0,
    #ChKP = [[8400, 5000, 25, 100, 450]]
    ChKP=[[8000, 4000, 100, 100, 100]]


    sf = Convolution(param_RSA, "example", "example", "Компакт", ChKP_param=[], ROI=[8000, 4000, 4000, 2000])
    sf.range_convolution_ChKP()
    sf.azimuth_convolution_ChKP()


    # sf.azimuth_convolution_ChKP(ROI=[0, 2000, 20000, 2000], path_input_rpt="C:/Users/X/Desktop/185900/1_with_1ChKP.rpt")
    
    '''{'Количество комплексных отсчетов': 11008, 
    'Количество зарегистрированных импульсов': 165500, 
    'Частота дискретизации АЦП': 400000000.0, 
    'Длина волны': 0.0351, 
    'Период повторения импульсов': 0.000485692, 
    'Ширина спектра сигнала': 300000000.0, 
    'Длительность импульса': 1e-05, 
    'Скорость движения носителя': 108, 
    'Размер антенны по азимуту': 0.23, 
    'Минимальная наклонная дальность': 2250, 
    'Коэффициент сжатия': 0.3, 
    'Минимальное значение РЛИ': 0, 
    'Максимальное значение РЛИ': 50922688, 
    'Значение квантиля': 412635.84375, 
    'Коэффициент сигнал/фон': 6.53, 
    'Значение фона в дБ': -12}'''
