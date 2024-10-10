import sys
from pathlib import Path
from time import sleep
from typing import Optional

from loguru import logger

from sync_services import SyncService
from utils import get_local_files
from exceptions import RequestError, APIUrlsError, NotFoundHostPathError


class SyncApp:
    """
    Приложение для синхронизации локальных файлов с удаленным хранилищем.

    Сравнивает файлы по MD5-хэшу.

    Атрибуты:
        _files_local (dict[str, str]): Словарь для хранения локальных файлов (название файла и MD5-хэш файла).
        _path_local (Path): Путь к локальному хранилищу.
        _client (SyncService): Клиент для взаимодействия с удаленным хранилищем.
    """

    _files_local: dict[str, str] = {}

    def __init__(self, path_local: Path, client: SyncService):
        """
        Инициализация SyncApp.

        Аргументы:
            path_local (Path): Путь к локальному хранилищу.
            client (SyncService): Клиент для взаимодействия с удаленным хранилищем.
        """

        self._path_local = path_local
        self._client = client

    def _get_host_files(self, debug_timeout: int) -> dict[str, str]:
        """
        Получает словарь локальных файлов и их MD5-хешей.

        Если возникает ошибка, функция повторяет попытку получения списка файлов.
        Если возникает ошибка FileNotFoundError, функция завершает работу приложения с кодом 1.

        Аргументы:
            path_local (Path): Путь к локальной директории, где находятся файлы.

        Возвращает:
            dict[str, str]: Словарь, где ключом является имя файла,
            а значением — его MD5-хеш.

        Исключения:
            FileNotFoundError: Если указанная директория не найдена.
        """

        while True:
            try:
                result = self._client.get_info()
            except NotFoundHostPathError as exc:
                logger.error(
                    "ОШИБКА. Не удалось получить список файлов с удаленного хранилища. {}".format(
                        exc
                    )
                )
                sys.exit(1)
            except (RequestError, APIUrlsError, Exception) as exc:
                logger.error(
                    "ОШИБКА. Не удалось получить список файлов с удаленного хранилища. {}".format(
                        exc
                    )
                )
                sleep(debug_timeout)
            else:
                return result

    def _delete(self, filename: str, debug_timeout: int) -> None:
        """
        Удаляет файл из удаленного хранилища.

        Если возникает ошибка при удалении файла, будет осуществлена повторная попытка через указанный интервал.

        Аргументы:
            filename (str): Имя файла для удаления.
            debug_timeout (int): Время ожидания перед повторной попыткой в случае ошибки.
        """

        while True:
            try:
                self._client.delete(filename)
            except (RequestError, APIUrlsError, Exception) as exc:
                logger.error("ОШИБКА. Файл {!r} не удален. {}".format(filename, exc))
                sleep(debug_timeout)
            else:
                logger.info("Файл {!r} успешно удален.".format(filename))
                return

    def _reload(self, filename: str, debug_timeout: int) -> None:
        """
        Обновляет файл в удаленном хранилище.

        Если возникает ошибка при обновлении файла, будет осуществлена повторная попытка через указанный интервал.

        Аргументы:
            filename (str): Имя файла для обновления.
            debug_timeout (int): Время ожидания перед повторной попыткой в случае ошибки.
        """

        while True:
            try:
                self._client.reload(path_local_file=self._path_local / filename)
            except FileNotFoundError:
                logger.error("ОШИБКА. Файл {!r} не найден.".format(filename))
            except (RequestError, APIUrlsError, Exception) as exc:
                logger.error("ОШИБКА. Файл {!r} не обновлен. {}".format(filename, exc))
                sleep(debug_timeout)
            else:
                logger.info("Файл {!r} успешно обновлен.".format(filename))
                return

    def _load(self, filename: str, debug_timeout: int) -> None:
        """
        Загружает файл в удаленное хранилище.

        Если возникает ошибка при загрузке файла, будет осуществлена повторная попытка через указанный интервал.

        Аргументы:
            filename (str): Имя файла для загрузки.
            debug_timeout (int): Время ожидания перед повторной попыткой в случае ошибки.
        """

        while True:
            try:
                self._client.load(path_local_file=self._path_local / filename)
            except FileNotFoundError:
                logger.error("ОШИБКА. Файл {!r} не найден.".format(filename))
            except (RequestError, APIUrlsError, Exception) as exc:
                logger.error("ОШИБКА. Файл {!r} не загружен. {}".format(filename, exc))
                sleep(debug_timeout)
            else:
                logger.info("Файл {!r} успешно загружен.".format(filename))
                return

    @classmethod
    def _set_logger(cls, debug: Optional[bool] = False) -> None:
        """
        Настраивает логирование приложения.

        Аргументы:
            debug (bool): Уровень логирования (True для DEBUG, иначе INFO).
        """

        format_logger = "{time: YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        logger.remove()
        logger.add(sys.stdout, level="DEBUG" if debug else "INFO", format=format_logger)

    def _check_host_files(self, files_host: dict[str, str], debug_timeout: int) -> None:
        """
        Проверяет наличие файлов на удаленном хранилище и удаляет отсутствующие,
        на локальной машине, файлы из удаленного хранилища.

        Аргументы:
            files_host (dict[str, str]): Словарь файлов на удаленном хранилище.
            debug_timeout (int): Время ожидания перед повторной попыткой в случае ошибки.
        """

        logger.debug("Начало итерации по списку файлов с удаленного хранилища.")
        logger.debug("files_host={}, self._files_local={}".format(files_host, self._files_local))
        for filename, f_datetime in files_host.items():
            if filename not in self._files_local:
                logger.debug(
                    "Файл {!r} отсутствует на локальном хранилище.".format(
                        filename
                    )
                )
                logger.info("Удаление файла {!r}.".format(filename))
                self._delete(filename=filename, debug_timeout=debug_timeout)
        logger.debug("Конец итерации по списку файлов с удаленного хранилища.")

    def _check_local_files(self, files_host: dict[str, str], debug_timeout: int) -> None:
        """
        Проверяет наличие локальных файлов и загружает отсутствующие файлы на удаленное хранилище,
        а также обновляет файлы с изменившимися MD5-хэшами.

        Аргументы:
            files_host (dict[str, str]): Словарь файлов на удаленном хранилище.
            debug_timeout (int): Время ожидания перед повторной попыткой в случае ошибки.
        """

        logger.debug("Начало итерации по списку файлов с локального хранилища.")
        logger.debug("files_host={}, self._files_local={}".format(files_host, self._files_local))
        for filename, f_md5hash in self._files_local.items():
            if filename in files_host:
                if f_md5hash != files_host[filename]:
                    logger.debug(
                        "Хэш md5 файлов {!r} не совпадают.".format(filename)
                    )
                    logger.info("Обновление файла {!r}".format(filename))
                    self._reload(filename=filename, debug_timeout=debug_timeout)
            else:
                logger.debug(
                    "Файл {!r} отсутствует на удаленном хранилище.".format(
                        filename
                    )
                )
                logger.info("Загрузка файла {!r}.".format(filename))
                self._load(filename=filename, debug_timeout=debug_timeout)
        logger.debug("Конец итерации по списку файлов с локального хранилища.")

    def run(self, timeout: int, debug_timeout: int, debug: Optional[bool]):
        """
        Запускает приложение для синхронизации файлов.

        Бесконечно проверяет и синхронизирует файлы между локальным и удаленным хранилищем,
        ожидая заданное время между итерациями.

        Аргументы:
            timeout (int): Время ожидания между итерациями синхронизации.
            debug_timeout (int): Время ожидания при ошибках.
            debug (Optional[bool]): Уровень логирования (True для DEBUG).

         Примечание: Метод работает бесконечно до его принудительного завершения.
         При каждом цикле происходит проверка наличия изменений как в локальном,
         так и в удаленном хранилище.
         """

        self._set_logger(debug=debug)

        logger.info("Начало синхронизации.")
        while True:
            logger.debug("Обновление списка локальных файлов.")
            self._files_local = get_local_files(path_local=self._path_local, debug_timeout=debug_timeout)
            logger.debug("Список локальных файлов: {}".format(self._files_local))

            logger.debug("Обновление списка файлов на удаленном хранилище.")
            files_host = self._get_host_files(debug_timeout=debug_timeout)
            logger.debug("Список файлов на удаленном хранилище: {}".format(files_host))

            if self._files_local != files_host:
                logger.debug("Списки не совпадают.")
                self._check_host_files(files_host=files_host, debug_timeout=debug_timeout)
                self._check_local_files(files_host=files_host, debug_timeout=debug_timeout)
            else:
                logger.debug("Списки совпадают.")
            logger.debug("Программа ушла в ожидание на {} секунд.".format(timeout))
            sleep(timeout)
