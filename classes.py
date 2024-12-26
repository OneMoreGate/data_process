import os

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
            else:
                raise ValueError(f'subdirectory {i} is not exist in {self.main_folder}')
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