import numpy as np
from matplotlib import pyplot as plt
import scipy as sc
"""Модуль производит свертку голограммы подальности.

Исходными данными являются:
number_complex_readings - количество комплексных отсчетов;
number_registered_impulses - количествово зарегистрированных импульсов;
sampling_frequency - частота дискретизации АЦП;
wavelength - длина волны;
pulse_period - период повторения импульсов;
signal_spectrum_width - ширина спектра сигнала;
pulse_duration - длительность импульса;
file_path - путь до файла голограммы;
file_name - название файла голограммы (опционально);
"""


class Convolution():
    def __init__(self,
                 number_complex_readings: int,
                 number_registered_impulses,
                 sampling_frequency: int,
                 wavelength,
                 pulse_period,
                 signal_spectrum_width,
                 pulse_duration: int,
                 file_path: str,
                 file_name: str = '',
                 ) -> None:

        self.number_complex_readings = number_complex_readings
        self.number_registered_impulses = number_registered_impulses
        self.sampling_frequency = sampling_frequency
        self.wavelength = wavelength
        self.pulse_period = pulse_period
        self.signal_spectrum_width = signal_spectrum_width
        self.pulse_duration = pulse_duration
        self.file_path = file_path
        self.file_name = file_name
        # наибольшая степени двойки для отсчетов
        self.power_two = 2**number_complex_readings.bit_length()
        # уточнить
        self.N_otst = 40000
        self.Na = 90000

    def get_support_functions(self) -> None:

        # получение первой опорнай функции
        support_function_1 = np.zeros(self.power_two, dtype=np.complex128)
        # число отсчетов в импульсе
        number_pulse_readings = round(
            self.pulse_duration*self.sampling_frequency)
        for i in range(number_pulse_readings):
            # выражение для расчета фазы первой опорной функции
            phase = np.pi * self.signal_spectrum_width * \
                (i)**2/(number_pulse_readings*self.sampling_frequency) - \
                np.pi*self.signal_spectrum_width*(i)/self.sampling_frequency
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
            rgg_file.seek(2*self.number_complex_readings*self.N_otst, 0)
            # создание временного нового файла для свертки по вертекали
            new_file_path = self.file_path[:-3]+'rpt'
            # чтение фрейма файла
            new_part = np.frombuffer(rgg_file.read(
                2*self.number_complex_readings), dtype='uint8')
            # создание копии из буфера для возможности его редактивования
            new_part_copy = new_part.copy()
            # очистка буфера
            del new_part
            # формирование значений от -127 до +128 изменением формата
            new_part_copy = new_part_copy.astype('int8')
            # заполнение первых 128 значений нулем
            new_part_copy[:128] = 0
            # из удвоенного количества отсчетов дальности создается матрица в комплексном виде
            for i in range(self.number_complex_readings):
                stc[i] = complex(new_part_copy[2*i],
                                 new_part_copy[2*i+1])
            stc[self.number_complex_readings:self.power_two] = 0
            fft_stc = sc.fft.fft(stc)
            # создание свертки комплексного столбца и опорной функции
            svRG = fft_stc*self.ftt_support_function_2
            svRG = sc.fft.ifft(svRG)
            # создание фейма для записи
            write_frame = np.zeros(2*self.power_two)
            write_frame[0:self.power_two] = svRG.real
            write_frame[self.power_two:2*self.power_two] = svRG.imag

            with open(new_file_path, 'w') as rpt_file:

                '''for i in range(self.Na):
                    new_part = rgg_file.read(2*self.number_complex_readings)'''


if __name__ == '__main__':

    number_complex_readings = 10944+64
    number_registered_impulses = 165500
    sampling_frequency = 400e6
    wavelength = 0.0351
    pulse_period = 485.692e-6
    signal_spectrum_width = 300e6
    pulse_duration = 10e-6

    sf = Convolution(number_complex_readings,
                     number_registered_impulses,
                     sampling_frequency,
                     wavelength,
                     pulse_period,
                     signal_spectrum_width,
                     pulse_duration,
                     "C:/Users/X/Desktop/185900/1.rgg")

    sf.get_support_functions()
    sf.range_convolution()
