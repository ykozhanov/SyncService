import hashlib
from pathlib import Path
import sys

from loguru import logger


def get_local_files(path_local: Path, debug_timeout: int) -> dict[str, str]:
    """
    Получает словарь локальных файлов и их MD5-хешей.

    Функция перебирает все файлы в указанной директории и вычисляет их MD5-хеши.
    Если возникает ошибка FileNotFoundError, функция завершает работу приложения с кодом 1.

    Аргументы:
        path_local (Path): Путь к локальной директории, где находятся файлы.
        debug_timeout (int): Время ожидания перед повторной попыткой (не используется в текущей реализации).

    Возвращает:
        dict[str, str]: Словарь, где ключом является имя файла,
        а значением — его MD5-хеш.

    Исключения:
        FileNotFoundError: Если указанная директория не найдена.
    """

    while True:
        try:
            files = {
                file.name: get_md5(file_path=file)
                for file in path_local.iterdir()
                if file.is_file()
            }
            logger.debug(
                "Результат обновления списка локальных файлов: {}".format(
                    files
                )
            )
        except FileNotFoundError:
            logger.error("ОШИБКА. Локальная директория '{}' не найдена.".format(path_local))
            sys.exit(1)
        else:
            return files


def get_md5(file_path: Path):
    """
    Вычисляет MD5-хеш для указанного файла.

    Аргументы:
        file_path (Path): Путь к файлу, для которого нужно вычислить хеш.

    Возвращает:
        str: MD5-хеш файла в шестнадцатеричном формате.
    """

    md5_hash = hashlib.md5()

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)

    return md5_hash.hexdigest()
