from pathlib import Path

from loguru import logger

from app import SyncApp
from config import DEBUG, DEBUG_TIMEOUT, PATH_HOST_YANDEX, PATH_LOCAL, TIMEOUT, TOKEN
from sync_services import YandexDiskSyncService

if not PATH_LOCAL:
    logger.error("ОШИБКА. Укажите синхронизируемую локальную директорию.")
    raise ValueError
elif not TOKEN:
    logger.error("ОШИБКА. Укажите токен.")
    raise ValueError
elif not PATH_HOST_YANDEX:
    logger.error("ОШИБКА. Укажите синхронизируемую директорию на удаленном хранилище.")
    raise ValueError

path_local = Path(PATH_LOCAL)

client_yandex = YandexDiskSyncService(token=TOKEN, path_host=Path(PATH_HOST_YANDEX))
app_yandex = SyncApp(path_local=path_local, client=client_yandex)

if __name__ == "__main__":
    app_yandex.run(timeout=TIMEOUT, debug=DEBUG, debug_timeout=DEBUG_TIMEOUT)
