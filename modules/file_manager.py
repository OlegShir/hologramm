"""Фаил содержит функции для работы с файлами"""
import json, datetime, pickle, os.path

class FileWorker():
    def __init__(self, path: str) -> None:
        """Класс предназначен для работы с файловой системой. Он обеспечивает получение данных 
        о расположении проекта голограммы, а также считывания и записи необходимых JSON файлов.
        Аргументом класса является путь до файла проекта (*.png, *.rgg)."""
        
        # получаем путь к проекту
        file_path_prj = "/".join(path.split("/")[0:-1])
        # получаем полное имя файла
        file = path.split("/")[-1]
        # определяем расширения файла и его имя
        file_array = file.split(".")
        # в случае если в названии файла используется только одна точка для разделения типа
        if len(file_array) == 2:
            file_name, file_type = file_array
        # иначе объединяем все до последней точки
        else:
            file_name = ".".join(file_array[0:-1])
            file_type = file_array[-1]

        self.file_path_prj = file_path_prj
        self.file_name = file_name
        self.file_type = file_type
        self.json_file = f"{self.file_path_prj}/{self.file_name}.json"

    def get_info_file(self) -> tuple[str, str, str]:
        """Возвращает данные о пути до файла, имя файла и его расширение."""

        return self.file_path_prj, self.file_name, self.file_type
        

    def project_json_reader(self) -> tuple[str, dict]:
        """Метод считывает JSON файл проекта и возвращает название РСА и его параметры."""
        with open(self.json_file, "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            key = list(data.keys())[0]
            value = data[key]

            self.key = key
            
            return key, value


    def project_json_writer(self, RSA_name:str, RSA_param:dict) -> None:
        """Метод записывает JSON файл проекта."""
        self.key = RSA_name
        data = {self.key: RSA_param}
        with open(self.json_file, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False)

    def update_json_value(self, key_value:list, new_value:list) -> None:
        """Метод обновляет список значений key"""
        # Открываем JSON файл для чтения
        with open(self.json_file, 'r', encoding="utf-8") as file:
            data = json.load(file)

        # Обновляем значения ключей в словаре data
        for i in range(len(key_value)):
            # Проверяем, что индекс i существует в списке ключей
            if i < len(data[self.key]):
                data[self.key][key_value[i]] = new_value[i]

        # Открываем JSON файл для записи и записываем обновленные данные
        with open(self.json_file, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


class RSAKAWorker():
    def __init__(self, name_file: str) -> None:
        self.name_file = name_file
        self.check_file = os.path.exists(name_file) # True

    def read_type_RSAKA(self) -> list:
        type_RSAKA = []
        if self.check_file:
            try:
                with open(self.name_file, 'rb') as file:
                    data = pickle.load(file)

                    type_RSAKA = list(data.keys())

            except:
                return []
        
        type_RSAKA.insert(0, "")
                
        return type_RSAKA
    
    def read_param_RASKA(self, type_RSAKA:str)->list:
        with open(self.name_file, 'rb') as file:
            data = pickle.load(file)
            if type_RSAKA in list(data.keys()):
                param_RSA:list = data[type_RSAKA]
                return param_RSA
            else:
                return []
        

    def write_RSAKA(self, new_RSA_name:str, new_RSAKA_param: list) -> bool:
        
        existing_data = {}
        if self.check_file:
            with open(self.name_file, 'rb') as file:
                existing_data = pickle.load(file)
                # Проверяем что название добавляемого РСА нет в базе
                if new_RSA_name in list(existing_data.keys()):
                    # Если ключ уже существует, то обновляем его значение
                    existing_data[new_RSA_name] = new_RSAKA_param
                    with open(self.name_file, 'wb') as file:
                        pickle.dump(existing_data, file)
                    return True

        # Обновляем данные
        existing_data.update({new_RSA_name: new_RSAKA_param})

        # Записываем данные
        with open(self.name_file, 'wb') as file:
            pickle.dump(existing_data, file)

        self.check_file = True

        return True


    def delete_RSAKA(self, type_RSAKA:str) -> bool:
        
        existing_data = {}
        if self.check_file:
            with open(self.name_file, 'rb') as file:
                existing_data = pickle.load(file)

        existing_data.pop(type_RSAKA)

        with open(self.name_file, 'wb') as file:
            pickle.dump(existing_data, file)

        return True

def project_json_writer(parent):
    """Функция сохранения параметров свертки"""
    # формирование словаря ЧКП
    data_ChKP = {}
    for i in range(len(parent.ChKP_param)):                
        data_ChKP[f'{i+1}'] = {'Размер ЧКП по дальности': parent.ChKP_param[i][3],
                                'Размер ЧКП по азимуту': parent.ChKP_param[i][4],
                                'Мощность ЧПК': parent.ChKP_param[i][2],
                                'Координата ЧКП по оси x': parent.ChKP_param[i][0],
                                'Координата ЧКП по оси y': parent.ChKP_param[i][1],
                                }


    data = {
            'Дата синтезирования': f'{datetime.datetime.now()}',
            'РСА': '-',
            'Параметры РСА': {
                                'Количество комплексных отсчетов': parent.Ndn, 
                                'Количество зарегистрированных импульсов': parent.Na,
                                'Частота дискретизации АЦП':    parent.fcvant,
                                'Длина волны':   parent.lamb, 
                                'Период повторения импульсов':  parent.Tpi,
                                'Ширина спектра сигнала': parent.Fsp,
                                'Длительность импульса':    parent.Dimp, 
                                'Скорость движения носителя':   parent.movement_speed,
                                'Размер антенны по азимуту':  parent.AntX,
                                'Наклонная дальность': parent.R,
                            },
            'Путь до файла *.rpt': parent.path_output_rpt,
            'Количество добавленных ЧКП': len(parent.ChKP_param),
            'Параметры ЧКП': data_ChKP,
            'Другие параметры': 'Другие параметры',
            }

    # Открытие файла для записи
    with open(f'{parent.file_path[:-4]}.json', 'w', encoding='utf-8') as file:
        # Запись данных в файл в формате JSON
        json.dump(data, file, ensure_ascii=False)

if __name__ == "__main__":
    

    def save_dict_to_file(dictionary, filename):
        with open(filename, 'wb') as file:
         pickle.dump(dictionary, file)

    dict = {
    "КА_1": [
            9000.0,
            40.8,
            770000,
            5.7,
            1.4,
            7.98,
            10000.0,
            0.00001           ]
        }

    save_dict_to_file(dict, "RSAKA.rsa")

    work= RSAKAWorker("RSAKA.rsa")
    
    #print(work.write_RSAKA("КА_2", [9000, 121]))
    #print(work.delete_RSAKA("КА_2"))
    #print(work.read_type_RASKA())
