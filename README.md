# SyncService
Исполнитель: **Юрий Кожанов**

-------------------------------------------------------------------------------------

## Описание проекта
SyncApp — это приложение для синхронизации локальных файлов с удаленным хранилищем (в данном случае, Яндекс.Диск). 
Оно позволяет загружать, обновлять и удалять файлы на Яндекс.Диске, а также получать информацию о текущих файлах 
в удаленном хранилище.

## Содержание
- [Установка](#установка)
- [Запуск](#запуск)
- [Используемые инструменты](#используемые-инструменты)
- [Контакты](#контакты)

## Установка
### Шаг 1: Предварительная настройка
Перед использованием приложения убедитесь, что на Вашем устройстве (Linux-based OS) установлены:
- **python 3.12.6**

### Шаг 2: Клонируйте репозиторий
Клонируйте github репозиторий на Ваше устройство:
```bash
https://github.com/ykozhanov/SyncService.git
```

### Шаг 3: Установка зависимостей
**СОВЕТ**: Используйте виртуальное окружение!

Установите необходимые зависимости через команду: 
```bash
pip install -r requirements.txt
```

### Шаг 4: Получить токен Яндекс.Диска
Перейдите по [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=4d757d11250342e5b800aa9c7a41cf63) 
и войдите в аккаунт Яндекс, с которым хотите синхронизировать локальные файлы.
Скопируйте полученный токен, он вам понадобится в следующем шаге.

### Шаг 5: Настройка приложения
В директории с приложением создайте `.env` файл с переменными окружения. 
Описание переменных находится в файле `env.example`.

## Запуск
Запустите приложение через команду: 
```bash
python main.py
```

## Используемые инструменты
- [Python](https://www.python.org/) как основной язык программирования.

## Контакты
По вопросам проекта и другим вопросам связанным с используемыми в проекте инструментам 
можно писать на почту `ykozhanov97@gmail.com`
