import os
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.collections import LineCollection
import shutil
import pandas as pd 
import numpy as np 



class Folder():
    # инициализация, проверка существования папки, проверка пустоты папки
    def __init__(self, main_folder: str) -> None:
        if not os.path.exists(main_folder):
            raise FileNotFoundError(f'directory \'{main_folder}\' is not exist')
        elif  (len(os.listdir(main_folder)) == 0):
            raise ValueError(f'directory \'{main_folder}\' is empty')
        else:
            self.main_folder = main_folder
            self._list_of_subdirs = os.listdir(main_folder)
            self.main_file_path = os.path.abspath(main_folder)
            
    # поиск всех вложенных директорий в основной папке
    def _find_subdirectories(self) -> None:
        self._subdirs_list = set()
        for i in self._list_of_subdirs:
            if os.path.isdir('\\'.join([self.main_folder, i])):
                self._subdirs_list.add(f'{i}')

    # составление списка header файлов в основной папке
    def _find_headers(self) -> None:
        self._headers_list = set()
        for catalog in self._list_of_subdirs:
            splited_catalog = catalog.split('.')[-1]
            if splited_catalog == 'header':
                self._headers_list.add(catalog.replace('.header', ''))

    # считывание данных об измерениях из файлов во вложенных директориях
    def _measurments_in_subdirectories(self) -> None:
        self._find_subdirectories()
        if len(self._subdirs_list) == 0:
            raise ValueError(f'directory \'{self.main_folder}\' does not contain subdirectories')
        self._all_measurs_from_subdirs = {}
        for i in self._subdirs_list:
            subdir_catalogs_list = [i.replace('.data', '') for i in os.listdir('\\'.join([self.main_folder, i]))]
            self._all_measurs_from_subdirs[i] = subdir_catalogs_list
        
    # считывание данных об измерениях из header файлов
    def _measurments_in_headers(self)-> None:
        self._find_headers()
        if len(self._headers_list) == 0:
            raise ValueError(f'directory \'{self.main_folder}\' does not contain header\'s files')
        splite_line = '______________________________________________________'
        self._all_measurs_from_headers = {}
        self._all_types_from_headers = {}
        for i in self._headers_list:
            self._all_measurs_from_headers[i] = set()
            self._all_types_from_headers[i] = {}
            with open('\\'.join([self.main_folder, i + '.header'])) as file:
                header_lines = []
                for k in file.readlines()[:-2]:
                    header_lines.append(k.replace('\n', ''))
            for j in range(len(header_lines)):
                if header_lines[j] == splite_line:
                    measurment_number, *measurmet_type = header_lines[j + 3].split()
                    self._all_measurs_from_headers[i].add(measurment_number)
                    self._all_types_from_headers[i][measurment_number] = ' '.join(measurmet_type)
                else:
                    continue

    # поиск пересечений в данных об измерениях и добавление данных о типе измерений
    def _create_dict_of_measurments(self)-> dict:
        self._measurments_in_subdirectories()
        self._measurments_in_headers()
        subdirectories = list(self._headers_list & self._subdirs_list)
        intersected_dict = {}
        for i in subdirectories:
            intersected_dict[i] = sorted(list(self._all_measurs_from_headers[i] & set(self._all_measurs_from_subdirs[i])))
        self.dict_of_measurments = {}
        for folder in list(intersected_dict.keys()):
            self.dict_of_measurments[folder] = {}
            dict_from_folder = {}
            for measur in intersected_dict[folder]:
                dict_from_folder[measur] =  self._all_types_from_headers[folder][measur]
            self.dict_of_measurments[folder] = dict_from_folder
    
    # получение названия итоговых папок
    def get_folders_name(self) -> list:
        if hasattr(self, 'dict_of_measurments'):
            return list(self.dict_of_measurments.keys())
        else:
            self._create_dict_of_measurments()
            return list(self.dict_of_measurments.keys())

    # удаление папки или папок
    def delete_folders_from_dict(self, folders_name: str | list, return_dict: bool = False) -> dict | None:
        if not hasattr(self, 'dict_of_measurments'):
            self._create_dict_of_measurments()
        folders_from_dict = list(self.dict_of_measurments.keys())
        existed_folders = []
        # проверка типов и существования
        if not isinstance(folders_name, list):
            folders_name = [folders_name]
        for i in folders_name:
            if not isinstance(i, str):
                try:
                    i = str(i)
                except:
                    raise TypeError(f'{i} is not {str} or can\'t be converted to {str}')
            if i in folders_from_dict:
                existed_folders.append(i)
        for i in existed_folders:
            del self.dict_of_measurments[i]
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
    
    def get_dict_of_single_folder(self):
        pass

    def delete_measures_from_folder(self):
        pass
    

class Data():
     
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
