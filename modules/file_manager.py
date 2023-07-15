"""Фаил содержит функции для работы с файлами"""
import json, datetime

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

    def get_info_file(self) -> tuple[str, str, str]:
        """Возвращает данные о пути до файла, имя файла и его расширение."""

        return self.file_path_prj, self.file_name, self.file_type
        

    def project_json_reader(self) -> tuple[str, list]:
        """Метод считывает JSON файл проекта и возвращает название РСА и его параметры."""
        with open(f"{self.file_path_prj}/{self.file_name}.json", "r", encoding="utf-8") as read_file:
            json_file = json.load(read_file)
            RSA_name = list(json_file.keys())[0]
            RSA_param = list(json_file.values())[0]
       
        return RSA_name, RSA_param

    def project_json_writer(self, RSA_name:str, RSA_param:list) -> None:
        """Метод записывает JSON файл проекта."""
        data = {RSA_name: RSA_param}
        with open(f"{self.file_path_prj}/{self.file_name}.json", "w", encoding="utf-8") as write_file:
            json.dump(data, write_file)



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

