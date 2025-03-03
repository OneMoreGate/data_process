from matplotlib import axes
from matplotlib import colormaps
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd 
import numpy as np 
import os
import shutil

class DC_IV():
    # инициализация, проверка существования папки, проверка пустоты папки
    def __init__(self, sample: str):
        if not os.path.exists(sample):
            raise FileNotFoundError(f'directory \'{sample}\' is not exist')
        elif  len(os.listdir(sample)) == 0:
            raise ValueError(f'directory \'{sample}\' is empty')
        else:
            self.__sample_name = str(sample)
            self.__sample_path = os.path.abspath(sample)
            self.__collect_full_dict()

    # поиск всех вложенных директорий в основной папке (поиск контактов, на которых проводились измерения)
    def __find_contacts(self) -> None:
        self.__contacts_list = []
        for i in os.listdir(self.__sample_path):
            if os.path.isdir(os.path.join(self.__sample_path, i)):
                self.__contacts_list.append(f'{i}')
        if len(self.__contacts_list) == 0:
            raise ValueError(f'\'{self.__sample_path}\' does not contain subdirectories')

    # проверка, что файл с данными типа .data (отсекаем остальные файлы, если имеются)
    def __is_data(self, data_file_path: str) -> bool:
        if data_file_path.split('.')[-1] == 'data':
            return True
        else:
            return False
        
    # создание пути из названия папок
    def __join_path(self, path_list: list[str]) -> str:
        return os.path.join(self.__sample_path, *path_list)
    
    # сбор информации о файлах, содержащих DC IV измерения в каждом контакте
    def __collect_full_dict(self) -> None:
        self.__find_contacts()
        self.__full_DC_IV_dict = {}
        for contact in self.__contacts_list:
            contact_files_list = []
            for file in os.listdir(self.__join_path([contact])):
                if self.__is_data(self.__join_path([contact, file])):
                    contact_files_list.append(file)
            if len(contact_files_list) == 0:
                continue
            contact_DC_IV_measurs = []
            for measure in contact_files_list:
                measure_path = self.__join_path([contact, measure])
                with open(measure_path) as file:
                    measur_type = file.readlines()[1]
                if 'DC IV' in measur_type:
                    contact_DC_IV_measurs.append(int(measure.replace('.data', '')))
                else:
                    continue
            self.__full_DC_IV_dict[contact] = sorted(contact_DC_IV_measurs)

    # удаление контакта или контактов из словаря с измерениями
    def delete_contacts(self, contacts_name: str | list) -> None:
        if not isinstance(contacts_name, list):
            contacts_name = [contacts_name]
        for contact in contacts_name:
            contact = str(contact)
            if contact in list(self.__full_DC_IV_dict.keys()):
                self.__contacts_list.remove(contact)
                del self.__full_DC_IV_dict[contact]
            else:
                print(f'contact {contact} not exist in {self.__sample_name}')

    # удаление измерений из контакта 
    def delete_measurments(self, contact: str | int, *args: int) -> None:
        contact = str(contact)
        if contact not in list(self.__full_DC_IV_dict.keys()):
            raise ValueError(f'contact {contact} not exist in {self.__sample_name}')
        will_be_del = set([i for i in [*args] if type(i) == int])
        for measur in will_be_del:
            if measur in self.__full_DC_IV_dict[contact]:
                self.__full_DC_IV_dict[contact].remove(measur)

    # возвращает список DC IV измерений с одного контакта 
    def get_contact_measurs(self, contact: str | int):
        contact = str(contact)
        if contact not in list(self.__full_DC_IV_dict.keys()):
            raise ValueError(f'contact {contact} not exist in {self.__sample_name}')
        else:
            return self.__full_DC_IV_dict[contact]

    # возврат полного словаря со всеми контактами и измерениямими 
    def get_full_dict(self)-> dict:
        return self.__full_DC_IV_dict
        
    # абсолютный путь к указанной папке
    def get_abspath(self) -> str:
        return self.__sample_path
    
    def get_contacts(self) -> list:
        return self.__contacts_list