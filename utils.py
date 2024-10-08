import hashlib
from pathlib import Path

from loguru import logger


def get_local_files(path_local: Path) -> dict[str, str] | bool:
    """
    Получает словарь локальных файлов и их MD5-хешей.

    Аргументы:
        path_local (Path): Путь к локальной директории.

    Возвращает:
        dict[str, str]: Словарь, где ключом является имя файла,
        а значением — его MD5-хеш. В случае ошибки вернет False.
    """

    try:
        files = {
            file.name: get_md5(file_path=file)
            for file in path_local.iterdir()
            if file.is_file()
        }
    except FileNotFoundError:
        logger.error("ОШИБКА. Локальная директория '{}' не найдена.".format(path_local))
        return False
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
