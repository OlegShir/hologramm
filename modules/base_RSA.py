import json
import sqlite3
import os
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
    def __init__(self, type: str, name: str) -> None:
        if type == 'SQL':
            self.connect = SQL_connect(name)
        if type == 'json':
            self.connect = Json_connect(name)


class Json_connect():
    def __init__(self, name: str) -> None:
        with open(name, "r", encoding="utf-8") as read_file:
            self.json_file = json.load(read_file)

    def get_list_RSA(self) -> list:
        list_RSA = []
        for key in self.json_file:
            list_RSA.append(key)

        return list_RSA

    def get_list_param_RLS(self, RLS_name: str) -> list:
        list_param_RLS = self.json_file[RLS_name]

        return list_param_RLS

    def get_info_RSA(self) -> str:
        info_RSA = self.json_file.get('RSA_type', False)

        return info_RSA


class SQL_connect():
    def __init__(self, name: str) -> None:
        self.con = sqlite3.connect(name)
        self.cur = self.con.cursor()

    def get_list_RSA(self) -> list:
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

    def get_info_RSA(self):
        pass

if __name__ == '__main__':
    q = Adapter('json', 'example_prj/sample.json')
    print(q.connect.get_info_RSA())
