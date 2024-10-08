import sys
from pathlib import Path
from time import sleep
from typing import Optional

from loguru import logger

from sync_services import SyncService
from utils import get_local_files


class SyncApp:
    """
    Приложение для синхронизации локальных файлов с удаленным хранилищем.

    Сравнивает файлы по MD5-хэшу.

    Атрибуты:
        _files_local (dict): Словарь для хранения локальных файлов (название файла и MD5-хэш файла).
        _path_local (Path): Путь к локальному хранилищу.
        _client (SyncService): Клиент для взаимодействия с удаленным хранилищем.
    """

    _files_local: dict[str, str] | bool = {}

    def __init__(self, path_local: Path, client: SyncService):
        """
        Инициализация SyncApp.

        Аргументы:
            path_local (Path): Путь к локальному хранилищу.
            client (SyncService): Клиент для взаимодействия с удаленным хранилищем.
        """

        self._path_local = path_local
        self._client = client

    def _get_host_files(self) -> dict[str, str] | bool:
        """
        Получает список файлов с удаленного хранилища.

        Возвращает:
            dict[str, str]: Словарь с именами файлов и MD5-хэш файлов,
            или False в случае ошибки.
        """

        try:
            result = self._client.get_info()
        except Exception as exp:
            logger.error(
                "ОШИБКА. Не удалось получить список файлов с удаленного хранилища. {}".format(
                    exp
                )
            )
            return False
        else:
            return result

    def _delete(self, filename: str):
        """
        Удаляет файл из удаленного хранилища.

        Аргументы:
            filename (str): Имя файла для удаления.

        Возвращает:
            bool: True, если файл успешно удален, иначе False.
        """

        try:
            self._client.delete(filename)
        except Exception as exp:
            logger.error("ОШИБКА. Файл {!r} не удален. {}".format(filename, exp))
            return False
        else:
            logger.info("Файл {!r} успешно удален.".format(filename))
            return True

    def _reload(self, filename: str):
        """
        Обновляет файл в удаленном хранилище.

        Аргументы:
            filename (str): Имя файла для обновления.

        Возвращает:
            bool: True, если файл успешно обновлен, иначе False.
        """

        try:
            self._client.reload(path_local_file=self._path_local / filename)
        except Exception as exp:
            logger.error("ОШИБКА. Файл {!r} не обновлен. {}".format(filename, exp))
            return False
        else:
            logger.info("Файл {!r} успешно обновлен.".format(filename))
            return True

    def _load(self, filename: str):
        """
        Загружает файл в удаленное хранилище.

        Аргументы:
            filename (str): Имя файла для загрузки.

        Возвращает:
            bool: True, если файл успешно загружен, иначе False.
        """

        try:
            self._client.load(path_local_file=self._path_local / filename)
        except Exception as exp:
            logger.error("ОШИБКА. Файл {!r} не загружен. {}".format(filename, exp))
            return False
        else:
            logger.info("Файл {!r} успешно загружен.".format(filename))
            return True

    @classmethod
    def _set_logger(cls, debug: Optional[bool] = False):
        """
        Настраивает логирование приложения.

        Аргументы:
            debug (bool): Уровень логирования (True для DEBUG, иначе INFO).
        """
        format_logger = "{time: YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        logger.remove()
        logger.add(sys.stdout, level="DEBUG" if debug else "INFO", format=format_logger)

    def run(self, timeout: int, debug_timeout: int, debug: Optional[bool]):
        """
        Запускает приложение для синхронизации файлов.

        Бесконечно проверяет и синхронизирует файлы между локальным и удаленным хранилищем.

        Аргументы:
            timeout (int): Время ожидания между итерациями синхронизации.
            debug_timeout (int): Время ожидания при ошибках.
            debug (bool): Уровень логирования (True для DEBUG).
        """

        self._set_logger(debug=debug)
        logger.info("Начало синхронизации.")
        while True:
            logger.debug("Обновление списка локальных файлов.")

            while True:
                self._files_local = get_local_files(self._path_local)
                logger.debug(
                    "Результат обновления списка локальных файлов: {}".format(
                        self._files_local
                    )
                )
                if isinstance(self._files_local, dict):
                    break
                sleep(debug_timeout)

            logger.debug("Список локальных файлов: {}".format(self._files_local))

            logger.debug("Обновление списка файлов на удаленном хранилище.")
            while True:
                files_host = self._get_host_files()
                logger.debug(
                    "Список файлов на удаленном хранилище: {}".format(files_host)
                )
                if isinstance(files_host, dict):
                    break
                sleep(debug_timeout)

            if self._files_local != files_host:
                logger.debug(
                    "Списки не совпадают. \nНачало итерации по списку файлов с удаленного хранилища."
                )

                for filename, f_datetime in files_host.items():

                    if filename not in self._files_local:
                        logger.debug(
                            "Файл {!r} отсутствует на локальном хранилище.".format(
                                filename
                            )
                        )
                        logger.info("Удаление файла {!r}.".format(filename))

                        while True:
                            if self._delete(filename=filename):
                                break
                            else:
                                sleep(debug_timeout)

                logger.debug("Начало итерации по списку файлов с локального хранилища.")
                for filename, f_datetime in self._files_local.items():
                    if filename in files_host:

                        if f_datetime != files_host[filename]:
                            logger.debug(
                                "Хэш md5 файлов {!r} не совпадают.".format(filename)
                            )
                            logger.info("Обновление файла {!r}".format(filename))

                            while True:
                                if self._reload(filename=filename):
                                    break
                                else:
                                    sleep(debug_timeout)

                    else:
                        logger.debug(
                            "Файл {!r} отсутствует на удаленном хранилище.".format(
                                filename
                            )
                        )
                        logger.info("Загрузка файла {!r}.".format(filename))

                        while True:
                            if self._load(filename=filename):
                                break
                            else:
                                sleep(debug_timeout)

            else:
                logger.debug("Списки совпадают.")
            logger.debug("Программа ушла в ожидание на {} секунд.".format(timeout))
            sleep(timeout)
