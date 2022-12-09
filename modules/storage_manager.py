import json
import sqlite3
'''
Количество комплексных отсчетов в канале дальности РГГ (в 1 импульсе) number_complex_readings
Количество зарегистрированных импульсов number_registered_impulses
Частота дискретизации АЦП sampling_frequency
Длина волны wavelength
Период повторения импульсов pulse_period
Ширина спектра сигнала signal_spectrum_width
Длительность импульса pulse_duration

'''


class Adapter():
    def __init__(self, type) -> None:
        if type == 'SQL':
            self.con = sqlite3.connect('RLS.db')
            self.cur = self.con.cursor()

    def get_list_RLS(self) -> list:
        '''Получение списка наименований РСЛ'''
        respone = self.cur.execute('SELECT RLS_name FROM RLS_param').fetchall()
        list_values = [x[0] for x in respone]

        return list_values

    def get_list_param_RLS(self, RLS_name: str) -> list:
        '''Получение параметров '''
        respone = self.cur.execute(
            'SELECT * FROM RLS_param WHERE RLS_name=?', (RLS_name,)).fetchall()
        list_values = [x for x in respone[0][1:]]

        return list_values

if __name__ == '__main__':
    db = SQLighter()
    print(db.get_list_param_RLS('f1'))
