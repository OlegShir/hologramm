"""Фаил содержит функции для работы с файлами"""
import json


def get_file_parameters(path: str):
    """Функция получения параметров (путь, имя и т.д"""
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
        

def project_json_reader(path_json: str, param: str):
    with open(path_json, "r", encoding="utf-8") as read_file:
        json_file = json.load(read_file)
    
    return json_file.get(param, '')
