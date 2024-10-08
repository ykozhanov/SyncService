from abc import ABC, abstractmethod
from pathlib import Path

import requests
from loguru import logger


class SyncService(ABC):
    """
    Абстрактный класс для синхронизации файлов с удаленным хранилищем.

    Атрибуты:
        _path_host (Path): Путь к удаленному хранилищу.
    """

    @abstractmethod
    def __init__(self, path_host: Path):
        """
        Инициализация SyncService.

        Аргументы:
            path_host (Path): Путь к удаленному хранилищу.
        """

        self._path_host = path_host

    @abstractmethod
    def load(self, path_local_file: Path) -> bool:
        """
        Загружает файл в удаленное хранилище.

        Аргументы:
            path_local_file (Path): Путь к локальному файлу.

        Возвращает:
            bool: True, если загрузка успешна, иначе False.
        """

        pass

    @abstractmethod
    def reload(self, path_local_file: Path) -> bool:
        """
        Обновляет файл в удаленном хранилище.

        Аргументы:
            path_local_file (Path): Путь к локальному файлу.

        Возвращает:
            bool: True, если обновление успешна, иначе False.
        """

        pass

    @abstractmethod
    def delete(self, filename: str) -> bool:
        """
        Удаляет файл из удаленного хранилища.

        Аргументы:
            filename (str): Имя файла для удаления.

        Возвращает:
            bool: True, если файл успешно удален, иначе False.
        """

        pass

    @abstractmethod
    def get_info(self) -> dict[str, str]:
        """
        Получает информацию о файлах в удаленном хранилище.

        Возвращает:
            dict[str, str]: Словарь с именами файлов и их MD5-хешами.
        """

        pass


class YandexDiskSyncService(SyncService):
    """
    Класс для синхронизации с Яндекс.Диском.

    Атрибуты:
        _urls (dict): URL-адреса для работы с API Яндекс.Диска.
        _token (str): Токен авторизации для доступа к API.
        _headers (dict): Заголовки для HTTP-запросов.
    """

    _urls = {
        "load": "https://cloud-api.yandex.net/v1/disk/resources/upload?path={}&overwrite={}",
        "get_info": "https://cloud-api.yandex.net/v1/disk/resources?path={}&fields=_embedded.items",
        "delete": "https://cloud-api.yandex.net/v1/disk/resources?path={}",
    }

    def __init__(self, token: str, path_host: Path):
        """
        Инициализация YandexDiskSyncService.

        Аргументы:
            token (str): Токен авторизации для доступа к Яндекс.Диску.
            path_host (Path): Путь к удаленному хранилищу на Яндекс.Диске.
        """

        super().__init__(path_host=path_host)
        self._token = "OAuth {}".format(token)
        self._headers = {"Authorization": self._token}

    def load(self, path_local_file: Path) -> bool:
        """
        Загружает файл в Яндекс.Диск.

        Аргументы:
            path_local_file (Path): Путь к локальному файлу.

        Возвращает:
            bool: True, если загрузка успешна, иначе выбрасывает исключение.

        Исключения:
            Exception: Если загрузка не удалась.
        """

        url = self._urls.get("load")

        if not url:
            raise ValueError(
                "ОШИБКА. Внутренняя ошибка приложения. Не найдено URL для работы с API в urls."
            )

        url = url.format(self._path_host / path_local_file.name, False)

        get_url_for_load = requests.get(url=url, headers=self._headers)
        data_get_url_for_load = get_url_for_load.json()
        url_for_load = data_get_url_for_load["href"]

        with open(path_local_file, "rb") as f:
            response = requests.put(url=url_for_load, data=f)

        if response.status_code == 201:
            return True
        else:
            data = response.json()
            raise Exception(data["message"])

    def reload(self, path_local_file: Path) -> bool:
        """
        Обновляет файл в Яндекс.Диске.

        Аргументы:
            path_local_file (Path): Путь к локальному файлу.

        Возвращает:
            bool: True, если обновление успешна, иначе выбрасывает исключение.

        Исключения:
            Exception: Если обновление не удалось.
        """

        url = self._urls.get("load")

        if not url:
            raise ValueError(
                "ОШИБКА. Внутренняя ошибка приложения. Не найдено URL для работы с API в urls."
            )

        url = url.format(self._path_host / path_local_file.name, True)

        get_url_for_reload = requests.get(url=url, headers=self._headers)
        data_get_url_for_reload = get_url_for_reload.json()
        url_for_reload = data_get_url_for_reload["href"]

        with open(path_local_file, "rb") as f:
            response = requests.put(url=url_for_reload, data=f)

        if response.status_code == 201:
            return True
        else:
            data = response.json()
            raise Exception(data["message"])

    def delete(self, filename: str) -> bool:
        """
        Удаляет файл из Яндекс.Диска.

        Аргументы:
            filename (str): Имя файла для удаления.

        Возвращает:
            bool: True, если файл успешно удален, иначе выбрасывает исключение.

         Исключения:
             Exception: Если удаление не удалось.
        """

        path_file = self._path_host / filename
        url = self._urls.get("delete")

        if not url:
            raise ValueError(
                "ОШИБКА. Внутренняя ошибка приложения. Не найдено URL для работы с API в urls."
            )

        url = url.format(path_file)

        response = requests.delete(url=url, headers=self._headers)

        if response.status_code == 204:
            return True
        else:
            data = response.json()
            raise Exception(data["message"])

    def get_info(self) -> dict[str, str]:
        """
        Получает информацию о файлах на Яндекс.Диске.

        Возвращает:
            dict[str, str]: Словарь с именами файлов и их MD5-хешами.

        Исключения:
            Exception: Если получение информации не удалось.
        """

        url = self._urls.get("get_info")

        if not url:
            raise ValueError(
                "ОШИБКА. Внутренняя ошибка приложения. Не найдено URL для работы с API в urls."
            )

        url = url.format(self._path_host)

        response = requests.get(url=url, headers=self._headers)
        data = response.json()

        logger.debug("Полученные данные с удаленного хранилища: {}".format(data))

        if response.status_code == 200:
            files_host = {
                file_info["name"]: file_info["md5"]
                for file_info in data["_embedded"]["items"]
                if file_info.get("type") == "file"
            }

            return files_host
        else:
            raise Exception(data["message"])
