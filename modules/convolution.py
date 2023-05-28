
"""Модуль производит свертку голограммы подальности.

Исходными данными являются:
Ndn - количество комплексных отсчетов;
Nazim - количествово зарегистрированных импульсов;
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
                 movement_speed: int = 108 # скорость носителя,
                 ) -> None:

        self.Ndn = Ndn
        self.Nazim = Nazim
        self.fcvant = fcvant
        self.lamb = lamb
        self.Tpi = Tpi
        self.Fsp = Fsp
        self.Dimp = Dimp
        self.file_path = file_path
        self.file_name = file_name
        self.movement_speed = movement_speed
        # расчетные выражения:
        # - наибольшая степени двойки для отсчетов
        self.power_two: int = 2**Ndn.bit_length()
        # - шаг по дальности
        dnr = 3e8/(2*self.fcvant)
        self.dnr = dnr
        # TODO: уточнить откуда берутся данные о self.N_otst и  self.Na
        # для ЧПК они повторяются 
        self.N_otst = 40000
        self.Na = 90000
        

    def get_support_functions(self) -> None:

        # получение первой опорнай функции
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
        # приминение БПФ к опорной функции
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
            # создание временного нового файла для свертки по вертекали
            new_file_path = self.file_path[:-3]+'rpt'
            with open(new_file_path, 'w') as rpt_file:
                for i in range(self.Na): 
                    # чтение фрейма файла
                    new_part_rgg_file = np.frombuffer(rgg_file.read(
                        2*self.Ndn), dtype='uint8')
                    # создание копии из буфера для возможности его редактивования
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
                    # создание фейма для записи
                    write_frame = np.zeros(2*self.power_two)
                    write_frame[0:self.power_two] = svRG.real
                    write_frame[self.power_two:2*self.power_two] = svRG.imag
                    



    def azimuth_convolution(self, preview: bool = True, x0: int=1):
        pass

    def range_convolution_ChKP(self,
                                sumRGGandChKP: bool = True, #если true - формируется суммарная РГГ, если false - то только ЧКП
                                impactChPK: bool = True, # показатель воздействия ЧПК
                                razmer_ChKP_r: int = 100, # pазмер ЧКП по наклонной дальности
                                razmer_ChKP_x: int = 450, # pазмер ЧКП по азимуту
                                AmpChkp: int = 25, # мощьность ЧПК без размера
                                X_ChKP: int = 8400, #  x координата ЧКП внутри исходной РГГ (в отсчетах)
                                Y_ChKP: int = 3190, # y координата ЧКП внутри исходной РГГ  (в отсчетах)
                                # TODO: откуда берутся данные
                                R: int = 4180, # наклонная дальность (до объекта прикрытия) R
                                AntX = 0.23, # размер антенны по азимуту                 
                                N_otst: int = 63000, # количество импульсов пропускаемых при чтении РГГ
                                Na: int = 90000    # количество считываемых импульсов
                                ) -> None:
             
        
        
        # расчет переменных
        # TODO: выражение использовалось ранее
        razr_r = razr_x = 3e8/(2*self.Fsp) # разрешение по наклонной дальности и азимуту, м razr_r
        dx = self.movement_speed*self.Tpi # Шаг по азимуту dx
        # расчет интервалa синтезирования
        Nas = np.fix(self.lamb*R/2/razr_x/dx) # QR
        Nas = int(np.fix(Nas/2)*2) # TODO: правильно?=> (5/2)*2 = 4 целое или точное, можно использоваь функцию math.trunc
        # ///////////
        Qx = self.lamb/AntX # ширина ДНА по азимуту
        QRm = Qx*R #  объем пространства, охватываемого радарным излучением TODO: почему в матлабе ссылка на количество считываемых импульсов Na?
        QR = int(np.fix(QRm/dx/2)*2) # количество секторов в объеме пространтва
        Las = Nas*dx # общвая ширина ДНА, которая представляет собой пространственную область или объем, охватываемый радарным излучением или приемом в горизонтальной плоскости
        Ts = Las/self.movement_speed # временной интервал, необходимый для охвата всей ширины ДНА во время движения
        x_max = dx*QR/2 # количество шагов азимута, которые укладываются в один интервал синтезирования
        rt_max = np.sqrt(R**2+x_max**2) # TODO: что за значение?
        ndop_max = int(np.fix((rt_max-R)/self.dnr)) # TODO: что за значение?   
            
        # SOLVE


        if sumRGGandChKP:
            # создание имени файла в зависимости от необходимой свертки
            if impactChPK:
                # фаил с результатами свертки по дальности суммарной РГГ (РГГ + ЧКП)
                output_file_path = f"{self.file_path[:-4]}_with_ChKP_{razmer_ChKP_r}_{razmer_ChKP_x}.rpt"
            else:
                # фаил с результатами свертки по дальности только исходной РГГ 
                output_file_path = f"{self.file_path[:-4]}.rpt"
        else:
            # фаил с результатами свертки по дальности только ЧКП
            # TODO: возможно в названии необходимо только оставить ЧКП
            output_file_path = f"{self.file_path[:-4]}_only_ChKP_{razmer_ChKP_r}_{razmer_ChKP_x}.rpt"

        if impactChPK:
            # формирование ЛЧМ сигнал для модели РГГ ЧКП
            N1 = int(self.Dimp*self.fcvant) # количествово дискретных отсчетов в ЛЧМ        
            _n = np.arange(N1)
            LCHM = np.pi * self.Fsp * (_n**2 / (N1 * self.fcvant) - _n / self.fcvant)
            w = 4*np.pi/self.lamb # TODO: непонятная переменная

            N_razb_r = razmer_ChKP_r/razr_r  # количествово разбиений РГГ по дальности
            N_razb_x = razmer_ChKP_x/razr_x # количествово разбиений РГГ по азимуту
            Nd_r = int(np.ceil(N1/N_razb_r)) # количествово когерентных отсчетов на одном участке разбиения по дальности    
            Nd_x = np.ceil(Nas/N_razb_x) # количествово когерентных отсчетов на одном участке разбиения по азимуту
            # TODO: уточнить переменные
            Fakt_razb_r = int(np.ceil(N1/Nd_r)) # Fakt_razb_r может отличаться от N_razb_r на +- 1
            Fakt_razb_x = int(np.ceil(QR/Nd_x)) # Для самолета Nas<<QR, следовательно Nd_x<<Fakt_razb_x
            Tau_koger_r = self.Dimp/N_razb_r  # интервал когерентности по дальности
            Tau_koger_x = Ts/N_razb_x  # интервал когерентности по азимуту
            dTp=0  # Показатель ввода ошибки синхронизации по ППИ (если dTp=0 ошибка не вводится) 
                   # TODO: нужен ли он
            Mdop=0 # TODO: уточнить переменные 
            '''
            # Формирование cлучайной функции ЧКП
            U_sl0 = np.zeros((N1, Fakt_razb_x)) # cоздается массив U_sl0 размером (N1, Fakt_razb_x) и заполняется нулями
            np.random.seed(2) # устанавливается начальное состояние генератора случайных чисел
            U = (np.random.rand(Fakt_razb_r, Fakt_razb_x) - 0.5) * 2 * np.pi # генерируется случайный массив
            #U_sl0[:, :Fakt_razb_x] = U[:N1, :] # значения из U копируются в соответствующую часть U_sl0, чтобы заполнить первые N1 строк
            for i in range(Fakt_razb_r):
                start_index = i * Nd_r
                end_index = (i + 1) * Nd_r
                U_sl0[start_index:end_index] = U[i]
            #del U # массив U удаляется, чтобы освободить память
            U_sl0 = U_sl0[:N1, :] # из U_sl0 выбираются только первые N1 строк.
            U_sl0_compl = np.cos(U_sl0) + 1j * np.sin(U_sl0) # создается массив U_sl0_compl, содержащий комплексные числа, полученные из U_sl0 с помощью тригонометрических функций
            #del U_sl0 # массив U_sl0 удаляется, чтобы освободить память

            # уточнение минимальных размеров РГГ ЧКП
            Nd_ChKP = np.ceil((N1 + ndop_max + 2 * Mdop) / 2) * 2
            Nd_ChKP = int(np.ceil(Nd_ChKP / 2) * 2)

            Rgg_ChKP = np.zeros((Nd_ChKP, QR), dtype=complex)
            ndop = np.zeros(QR, dtype=int)

            for i in range(QR):
                U_sl = np.zeros(Nd_ChKP, dtype=complex)
                Imp = np.zeros(Nd_ChKP, dtype=complex)
                x = (-QR/2 + i - 1) * dx
                rt = np.sqrt(R**2 + x**2)
                ndop[i] = int(np.fix((rt - R) / self.dnr))
                faza = LCHM + w * rt
                Imp0 = np.exp(1j * faza)
                Imp[ndop[i] + Mdop + 1:ndop[i] + Mdop + N1] = Imp0
                qq = np.ceil(i / Nd_x)
                U_sl[ndop[i] + Mdop + 1:ndop[i] + Mdop + N1] = U_sl0_compl[:, qq]
                Rgg_ChKP[:, i] = Imp * U_sl



            qq = np.ceil(np.arange(1, QR + 1) / Nd_x)  # cоздается массив qq, содержащий значения, полученные из деления последовательности от 1 до QR на Nd_x, округленные до ближайшего целого числа.
            U_sl = np.tile(U_sl0_compl[:, qq.astype(int) - 1], (1, QR)) # Создается массив U_sl путем повторения соответствующих столбцов из U_sl0_compl в соответствии с qq
            Rgg_ChKP = Imp[:, np.newaxis] * U_sl[ndop.astype(int) + Mdop, :] # Создается массив Rgg_ChKP путем поэлементного умножения Imp на соответствующие элементы из U_sl
            del U_sl0_compl, U_sl, Imp # массивы U_sl0_compl, U_sl и Imp удаляются, чтобы освободить память

            Rgg_ChKP *= AmpChkp # массив Rgg_ChKP умножается на мощьность ЧПК

            Y0, X0 = Rgg_ChKP.shape # Получаются размеры массива Rgg_ChKP.
            Rgg_ChKP2 = np.zeros((self.Ndn, X0)) # Увеличиваем размер РГГ ЧКП по наклонной дальности до размера реальной РГГ Nd
            Rgg_ChKP2[Y_ChKP:Y0 + Y_ChKP, :] = Rgg_ChKP # Смещаем центр РГГ ЧКП на требуемую координату Y_ChKP
            del Rgg_ChKP # массив Rgg_ChKP удаляется, чтобы освободить память
            '''

            N1 = int(np.fix(Dimp * self.fcvant))
            LCHM = np.zeros((N1, 1))
            w = 4 * np.pi / lamb

            
            U_sl0 = np.zeros((N1, Fakt_razb_x))
            s = 2
            np.random.seed(s)
            U = (np.random.rand(Fakt_razb_r, Fakt_razb_x) - 0.5) * 2 * np.pi

            for z in range(Fakt_razb_x):
                for G in range(Fakt_razb_r):
                    U_sl0[(G - 1) * Nd_r:G * Nd_r, z] = U[G, z]

            U_sl0 = U_sl0[:N1, :]
            U_sl0_compl = np.cos(U_sl0) + 1j * np.sin(U_sl0)
            
            Nd_ChKP = int(np.ceil((N1 + ndop_max + 2 * Mdop) / 2)) * 2
            Nd_ChKP = int(np.ceil(Nd_ChKP / 2)) * 2
            
            Rgg_ChKP = np.zeros((Nd_ChKP, QR), dtype=complex)

            ndop = np.zeros(QR, dtype=int)

            for i in range(QR):
                U_sl = np.zeros((Nd_ChKP,1), dtype=complex)
                Imp = np.zeros((Nd_ChKP,1), dtype=complex)
                x = (-QR / 2 + i - 1) * dx
                rt = np.sqrt(R ** 2 + x ** 2)
                ndop[i] = int(np.fix((rt - R) / self.dnr))
                faza = LCHM + w * rt
                Imp0 = np.exp(1j * faza)
                Imp[ndop[i] + Mdop:ndop[i] + Mdop + N1] = Imp0
                qq = int(np.ceil(i / Nd_x))
                U_sl[ndop[i] + Mdop:ndop[i] + Mdop + N1,i] = U_sl0_compl[:, qq]
                Rgg_ChKP[:, i] = Imp * U_sl

            Rgg_ChKP = Rgg_ChKP * AmpChkp
            Y0, X0 = Rgg_ChKP.shape
            Rgg_ChKP2 = np.zeros((self.power_two, X0), dtype=complex)
            Rgg_ChKP2[Y_ChKP:Y0 + Y_ChKP, :] = Rgg_ChKP

            del U_sl0_compl#, U_sl, Imp, Imp0

            # ====== Формирование ОФ для свертки зондирующего импульса ============
            opor = np.cos(LCHM) + 1j * np.sin(LCHM)  # фаза сигнала в комплексном виде
            opor1 = np.zeros((self.Ndn, 1))
            opor1[:N1] = opor

            N2 = N1 // 2
            opor2 = np.zeros((self.Ndn, 1))
            opor2[:N2] = opor1[N2:N1]
            opor2[N2:self.Ndn] = opor1[:N2]

            sp_OF = np.fft.fft(opor2)

            del opor, opor1, opor2, LCHM # массивы opor, opor1, opor2, LCHM удаляются, чтобы освободить память

            svRG = np.zeros(self.power_two)  # Инициализация массива размером Nd с нулями
            stc = np.zeros(self.power_two, dtype=complex)  # Инициализация массива размером Nd с комплексными числами
            with open(self.file_path, 'rb') as rgg_file, open(output_file_path, 'wb') as rpg_file:
                # поиск начала считывания информации
                rgg_file.seek(2*self.Ndn*self.N_otst, 0)
                b = 0
                count_progres = 0

                if sumRGGandChKP:
                    for i in range(1, Na + 1):
                        st = np.fromfile(rgg_file, dtype=np.uint8, count=Ndn*2)
                        st = np.where(st > 128, st - 256, st)  # Формирование значений от -127 до +128
                        st[:128] = 0

                        # Преобразование удвоенного количества отсчетов в столбец комплексных чисел
                        stc[:Ndn+1] = complex(st[0::2], st[1::2])
                        stc[Ndn+1:self.power_two] = 0

                        if impactChPK and X_ChKP - X0//2 < i <= X_ChKP + X0//2:
                            b += 1
                            stc += Rgg_ChKP2[:, b]

                        sp_stc = np.fft.fft(stc)
                        svRG = sp_stc * sp_OF  # Умножение спектров столбца на опорную функцию
                        svRG = np.fft.ifft(svRG)
                        Rg = np.concatenate((np.real(svRG), np.imag(svRG)))
                        Rg.astype(np.float32).tofile(rpg_file)  # Запись в файл
                        count_progres += 1  # Счетчик для отображения прогресса программы
                        print(count_progres)
                elif not sumRGGandChKP:
                    for i in range(1, X0 + 1):
                        stc = Rgg_ChKP2[:, i]

                        sp_stc = np.fft.fft(stc)
                        svRG = sp_stc * sp_OF  # Умножение спектров столбца на опорную функцию
                        svRG = np.fft.ifft(svRG)
                        Rg = np.concatenate((np.real(svRG), np.imag(svRG)))
                        Rg.astype(np.float32).tofile(rpg_file)  # Запись в файл
                        count_progres += 1  # Счетчик для отображения прогресса программы






        

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
    sf.range_convolution_ChKP()
