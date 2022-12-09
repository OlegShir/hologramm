"""Класс обеспечивает получение списка параметров РЛС, их изменение,
   добавление и удаление."""
from storage_manager import Adapter

class RLSControl():
    def __init__(self) -> None:
        # подключение к хранилищу
        self.adapter = self.adapter_storage()

    def adapter_storage(self) -> object:
        '''Aдаптер подключения к хранилищу'''
        adapter = Adapter('SQL')
        return adapter

    def get_list_RLS(self) -> list:
        '''Получение списка наименований РСЛ'''
        list_RLS = self.adapter.get_list_RLS()
        return list_RLS
    
    def get_list_param_RLS(self, RLS_name) -> list:
        '''Получение списка параметров выбранной РСЛ'''
        pass
    

    
