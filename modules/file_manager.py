"""Фаил содержит функции для работы с файлами"""
import json, datetime


def get_file_parameters(path: str):
    """ункция получФения параметров (путь, имя и т.д"""
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

    return file_path_prj, file_name, file_type
        

def project_json_reader(path_json: str, task: str):
    with open(path_json, "r", encoding="utf-8") as read_file:
        json_file = json.load(read_file)
        if task == "RSA":
            response = list(json_file.keys())[0]
        else:
            response = list(json_file.values())[0]
    
    return response

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
