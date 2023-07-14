import numpy as np
import time, random

class ChKPBuider():
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
            self.start_time = time.time()
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
                
                print(f'Сформирована {i+1}-я ЧКП, время: {np.round(time.time()-self.start_time, 2)} c.')
   
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
            # Rgg_ChKP2[ChKP_location_y:Y0 + ChKP_location_y, :] = Rgg_ChKP
            start_index = max(0, ChKP_location_y - Y0//2)
            end_index = min(start_index + Y0, self.RSA_param.power_two)

            Rgg_ChKP2[start_index:end_index, :] = Rgg_ChKP[:end_index-start_index, :]


            coord_ChKP = (ChKP_location_x, X0)
            return coord_ChKP, Rgg_ChKP2
