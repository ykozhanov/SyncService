import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = True if os.environ.get("DEBUG") == "True" else False
TOKEN = os.environ.get("TOKEN")
TIMEOUT = int(os.environ.get("TIMEOUT", 15))
DEBUG_TIMEOUT = int(os.environ.get("DEBUG_TIMEOUT", 3))
PATH_LOCAL = os.environ.get("PATH_LOCAL")
PATH_HOST_YANDEX = os.environ.get("PATH_HOST_YANDEX")
