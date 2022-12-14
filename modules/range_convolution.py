import numpy as np
from matplotlib import pyplot as plt
"""Модуль производит свертку голограммы подальности.

Исходными данными являются:
number_complex_readings - количество комплексных отсчетов;
number_registered_impulses - количествово зарегистрированных импульсов;
sampling_frequency - частота дискретизации АЦП;
wavelength - длина волны;
pulse_period - период повторения импульсов;
signal_spectrum_width - ширина спектра сигнала;
pulse_duration - длительность импульса;
"""


def convolution(number_complex_readings: int,
                number_registered_impulses,
                sampling_frequency: int,
                wavelength,
                pulse_period,
                signal_spectrum_width,
                pulse_duration: int) -> None:

    # наибольшая степени двойки для отсчетов
    power_two = number_complex_readings.bit_length()
    # уточнить
    N_otst = 40000
    Na = 90000

    # первая опорная функция
    support_function_1 = np.zeros(2**power_two, dtype=np.complex128)
    # число отсчетов в импульсе
    number_pulse_readings = round(pulse_duration*sampling_frequency)
    for i in range(number_pulse_readings):
        # выражение для расчета фазы первой опорной функции
        phase = np.pi * signal_spectrum_width * \
            (i-1)**2/(number_pulse_readings*sampling_frequency) - \
            np.pi*signal_spectrum_width*(i-1)/sampling_frequency
        # отсчет фазы сигнала в комплексном виде [cos(phase) + sin(phase)j]
        complex_value = complex(np.cos(phase), np.sin(phase))
        support_function_1[i] = complex_value

    # вторая опорная функция
    support_function_2 = np.zeros((2**power_two, 1), dtype=np.complex128)
    # число отсчетов в импульсе
    number_pulse_readings = round(number_pulse_readings/2)
    # сдвиг опорной функции для совмещения начала изображения (кадра)
    # с началом отсчетов
    for i in range(number_pulse_readings):
        support_function_2[i] = support_function_1[i+number_pulse_readings]
        support_function_2[i+2**power_two-number_pulse_readings] = support_function_1[i]
    ftt_support_function_2 = np.fft.fft(support_function_2)

    plt.figure()
    plt.plot(support_function_1.imag)
    plt.show()

    print(ftt_support_function_2[2],ftt_support_function_2[20], ftt_support_function_2[106])
    return support_function_1




if __name__ == '__main__':

    number_complex_readings = 10944+64
    number_registered_impulses = 165500
    sampling_frequency = 400e6
    wavelength = 0.0351
    pulse_period = 485.692e-6
    signal_spectrum_width = 300e6
    pulse_duration = 10e-6

    sf = convolution(number_complex_readings,
                     number_registered_impulses,
                     sampling_frequency,
                     wavelength,
                     pulse_period,
                     signal_spectrum_width,
                     pulse_duration)


