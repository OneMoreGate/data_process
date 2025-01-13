import os
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.collections import LineCollection
import shutil
import pandas as pd 
import numpy as np 



class Measurments():
    # инициализация, проверка существования папки, проверка пустоты папки
    def __init__(self, main_folder: str) -> None:
        if not os.path.exists(main_folder):
            raise FileNotFoundError(f'directory \'{main_folder}\' is not exist')
        elif  (len(os.listdir(main_folder)) == 0):
            raise ValueError(f'directory \'{main_folder}\' is empty')
        else:
            self.main_folder = main_folder
            self.list_of_subdirs = os.listdir(main_folder)
            self.main_file_path = os.path.abspath(main_folder)
            
    # поиск всех вложенных директорий в основной папке
    def _find_contacts_folder(self) -> None:
        self.contacts_list = set()
        for i in self.list_of_subdirs:
            if os.path.isdir('\\'.join([self.main_folder, i])):
                self.contacts_list.add(f'{i}')

    # проверка, что файл типа data
    def _is_data_file(self, path: str) -> bool:
        if path.split('.')[-1] == 'data':
            return True
        else:
            return False
    # создание пути из названия папок
    def _create_path(self, list: list[str]) -> str:
        return '\\'.join([self.main_file_path] + list)

    # считывание данных об измерениях из файлов во вложенных директориях
    def _create_dict_of_measurments(self, return_dict: bool = False) -> None | dict:
        self._find_contacts_folder()
        if len(self.contacts_list) == 0:
            raise ValueError(f'directory \'{self.main_folder}\' does not contain subdirectories')
        self.dict_of_measurments = {}
        for i in self.contacts_list:
            subdir_catalogs_list = [file for file in os.listdir(self._create_path([i])) if self._is_data_file(self._create_path([i, file]))]
            if len(subdir_catalogs_list) == 0:
                continue
            subdir_measurs_type = {}
            for j in subdir_catalogs_list:
                file_path = self._create_path([i, j])
                with open(file_path) as file:
                    measur_type = '_'.join(file.readlines()[1].split()[1:3])
                subdir_measurs_type[j.replace('.data', '')] = measur_type
            self.dict_of_measurments[i] = subdir_measurs_type
        if return_dict == True:
            return self.dict_of_measurments
        
    # возврат словаря с измерениями
    def get_dict_of_measurments(self)-> dict:
        if hasattr(self, 'dict_of_measurments'):
            return self.dict_of_measurments
        else:
            self._create_dict_of_measurments()
            return self.dict_of_measurments
        
    # абсолютный путь к указанной папке
    def get_abspath(self) -> str:
        return self.main_file_path
    
    # получение словаря только с одного контакта
    def get_contact_dict(self, contact_name: str | int) -> dict:
        if not hasattr(self, 'dict_of_measurments'):
            self._create_dict_of_measurments()
        elif str(contact_name) not in list(self.dict_of_measurments.keys()):
            raise ValueError(f'{contact_name} not exist in {self.main_folder}')
        return self.dict_of_measurments[str(contact_name)]
    
    # удаление папки или папок
    def delete_contacts(self, contact_name: str | list, return_dict: bool = False) -> dict | None:
        if not hasattr(self, 'dict_of_measurments'):
            self._create_dict_of_measurments()
        contact_from_dict = list(self.dict_of_measurments.keys())
        existed_contact = []
        # проверка типов и существования
        if not isinstance(contact_name, list):
            contact_name = [contact_name]
        for i in contact_name:
            if not isinstance(i, str):
                try:
                    i = str(i)
                except:
                    raise TypeError(f'{i} is not {str} or can\'t be converted to {str}')
            if i in contact_from_dict:
                existed_contact.append(i)
        for i in existed_contact:
            del self.dict_of_measurments[i]
        if return_dict == True:
            return self.dict_of_measurments
    
    # удаление измерений из контакта 
    def delete_measurments(self, del_dict: dict) -> None:
        if not hasattr(self, 'dict_of_measurments'):
            self._create_dict_of_measurments()
        del_dict_keys = list(del_dict.keys())
        all_dict_keys = list(self.dict_of_measurments.keys())
        for contact in del_dict_keys:
            if str(contact) in all_dict_keys:
                if not isinstance(del_dict[contact], list):
                    raise ValueError(f'dict values must be {list} type')
                for measur in del_dict[contact]:
                    if str(measur) in list(self.dict_of_measurments[str(contact)]):
                        self.dict_of_measurments[str(contact)].pop(str(measur), None)
                    else:
                        continue

            else:
                continue
    

class Draw_DC_IV():
     
    def __init__(self, folder: Folder) -> None:
        if isinstance(folder, Folder):
            self.folder = folder
            self.dict_of_measurs = self.folder.dict_of_measurments
        else:
            raise TypeError(f'Input must be {Folder} type')
        
    def _colored_line(self, voltage, current, c, ax: matplotlib.axes, **lc_kwargs):
        default_kwargs = {"capstyle": "butt"}
        default_kwargs.update(lc_kwargs)
        x = np.asarray(voltage)
        y = np.asarray(current)
        x_midpts = np.hstack((x[0], 0.5 * (x[1:] + x[:-1]), x[-1]))
        y_midpts = np.hstack((y[0], 0.5 * (y[1:] + y[:-1]), y[-1]))
        coord_start = np.column_stack((x_midpts[:-1], y_midpts[:-1]))[:, np.newaxis, :]
        coord_mid = np.column_stack((x, y))[:, np.newaxis, :]
        coord_end = np.column_stack((x_midpts[1:], y_midpts[1:]))[:, np.newaxis, :]
        segments = np.concatenate((coord_start, coord_mid, coord_end), axis=1)
        lc = LineCollection(segments, **default_kwargs)
        lc.set_array(c) 
        return ax.add_collection(lc)
        
    def get_single_DC_IV_data(self, subdirectory: str, file_name: str) -> pd.DataFrame:
        data_dir = self.folder.get_abspath() + '\\' + subdirectory + '\\' + file_name + '.data'
        if not os.path.exists(data_dir):
            raise ValueError(f'path {data_dir} is not exist')
        dataframe = pd.read_csv(data_dir, delimiter='   ', skiprows=16, engine='python', header=None, encoding='ISO-8859-1').astype(np.float32)
        dataframe.rename(columns = {0: 'voltage', 1: 'current', 2: 'resistance'}, inplace=True)
        return dataframe
    
    def draw_single_DC_IV_plot(self, voltage: pd.Series, current: pd.Series) -> None:
        data_len = len(voltage)
        fig, ax = plt.subplots(figsize = [10,5])
        ax.set_yscale('log')
        ax.grid(which='major', linewidth = 0.6)
        ax.grid(which='minor', linewidth = 0.2)
        ax.set_xlim(xmin= voltage.min()*1.2, xmax=voltage.max()*1.2)
        ax.set_ylim(ymin= current.min()*0.2, ymax=current.max()*5)
        color = np.linspace(0, 1, data_len)
        lines = self._colored_line(voltage, current, color, ax, cmap = 'plasma')
        cbar = fig.colorbar(lines)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['start','end'], size = 15)
        
    def _save_DC_IV_plot(self, subdirectory: str, file_name: str)-> None:
            if not hasattr(self, 'graphs_path'):
                local_graph_folder = self.folder.get_abspath()
            else:
                local_graph_folder = self.graphs_path + '\\' + subdirectory + '\\' + file_name + '.png'
            plt.savefig(local_graph_folder, bbox_inches = 'tight', dpi = 200)
            plt.close()

    def _create_dir(self, path: str) -> None:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            os.mkdir(path)
        else:
            os.mkdir(path)

    def draw_all_DC_IV(self, graphs_path: str)-> None:
        self.graphs_path = '\\'.join([os.path.dirname(self.folder.get_abspath()), graphs_path])
        self._create_dir(self.graphs_path)
        for folder in list(self.dict_of_measurs.keys()):
            local_graph_folder = '\\'.join([self.graphs_path, folder])
            self._create_dir(local_graph_folder)
            for measur in list(self.dict_of_measurs[folder].keys()):
                if self.dict_of_measurs[folder][measur] == 'DC IV':
                    data = self.get_single_DC_IV_data(folder, measur)
                    voltage = data['voltage']
                    current = np.abs(data['current'])
                    self.draw_single_DC_IV_plot(voltage, current)
                    self._save_DC_IV_plot(folder, measur)
                else:
                    continue
