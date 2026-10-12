# LoggerMixin

Лёгкая библиотека для логирования в Python с поддержкой ротации файлов и настройки уровня логирования через переменные окружения.

Позволяет подключить логгер к любому классу через наследование.

## Установка

Установка напрямую из GitHub:

```bash
pip install git+https://github.com/SameUsers/LoggerMixin.git
```

Или добавьте в `requirements.txt`:

```text
git+https://github.com/SameUsers/LoggerMixin.git
```

**Требования:** Python 3.11+

## Использование

```python
from logger_mixin import LoggerMixin


class Test(LoggerMixin):
    def __init__(self) -> None:
        super().__init__(logger_name="MyCustomLogger")

    def test(self) -> None:
        self._logger.info("Информационное сообщение")
        self._logger.warning("Предупреждение")
        self._logger.error("Ошибка")


test = Test()
test.test()
```

### Автоматическое имя логгера

Если не передавать `logger_name`, имя будет сформировано автоматически на основе модуля и названия класса.

```python
from logger_mixin import LoggerMixin


class Test(LoggerMixin):
    def __init__(self) -> None:
        super().__init__()
```

### Переопределение имени логгера

```python
super().__init__(logger_name="CustomLogger")
```

## Конфигурация

Настройка осуществляется через переменные окружения.

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `LOG_DIR` | Директория хранения логов | `logs` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

Пример `.env`:

```dotenv
LOG_DIR=logs
LOG_LEVEL=DEBUG
```

Переменные окружения должны быть загружены до инициализации логгера.

## Возможности

- Подключение через наследование `LoggerMixin`.
- Автоматическое создание логгера для класса.
- Возможность задать собственное имя логгера.
- Логирование в консоль и файл.
- Ротация лог-файлов.
- Настройка уровня логирования.
- Использование стандартного модуля `logging`.

## Ротация логов

По умолчанию используется `RotatingFileHandler`:

- Максимальный размер файла — 10 МБ.
- Количество резервных файлов — 5.


