# 🚀 OneC Contract Generator

[![PyPI version](https://badge.fury.io/py/onec-contract-generator.svg)](https://badge.fury.io/py/onec-contract-generator)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Autonomous system for generating structured JSON contracts from 1C:Enterprise configurations**

Полностью автономная система для генерации структурированных JSON-контрактов из конфигураций 1С, включая контракты метаданных объектов, форм и модулей.

## 📋 Возможности

- 🎯 **Контракты метаданных** - структурированное описание объектов (справочники, документы, обработки)
- 📋 **Контракты форм** - архитектура форм с элементами управления и атрибутами
- 🔧 **Контракты модулей** - описание модулей объектов с функциями и процедурами
- 🔍 **Группированные логи** - структурированный вывод результатов с группировкой по категориям
- 📊 **Статистика и отчеты** - анализ структуры конфигурации
- 🚀 **Интерактивный режим** - пошаговый мастер с подсказками
- ⚡ **Командный режим** - автоматизация через аргументы
- 🔍 **Semantic Search Ready** - оптимизированная структура для поисковых систем

## 🚀 Быстрый старт

### Установка

```bash
# Установка с PyPI
pip install onec-contract-generator
```

### Использование

#### Интерактивный режим (рекомендуется)

```bash
onec-contract-generate
```

Запустится пошаговый мастер:
1. 📁 Выбор директории конфигурации
2. 📄 Выбор файла отчета
3. 📂 Выбор выходной директории
4. 🔧 Выбор компонентов для генерации
5. 🎯 Подтверждение и запуск

#### Командный режим

```bash
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

#### Анализ контрактов

```bash
# Статистика
onec-contract-analyze --action stats

# Поиск
onec-contract-analyze --action search --query "ДокументыПредприятия"

# Валидация
onec-contract-analyze --action validate

# Экспорт отчета
onec-contract-analyze --action report --output analysis.md
```

#### Тестирование

```bash
# Запуск тестов
onec-contract-test

# Или с pytest
pytest tests/
```

## 🏗️ Структура проекта

```
onec-contract-generator/
├── src/                                    # Исходный код
│   ├── core/                               # Основные компоненты
│   │   ├── launcher.py                     # 🚀 Единый запускатор
│   │   ├── metadata_generator.py           # 📋 Генератор контрактов метаданных
│   │   ├── form_generator.py               # 📝 Генератор контрактов форм
│   │   └── module_generator.py             # 🔧 Генератор контрактов модулей
│   ├── utils/                              # Утилиты
│   └── parsers/                            # Парсеры
├── scripts/                                # Скрипты запуска
│   ├── generate.py                         # 🚀 Главный скрипт
│   ├── analyze.py                          # 📊 Скрипт анализа
│   ├── test.py                             # 🧪 Скрипт тестирования
│   └── publish.py                          # 📦 Скрипт публикации на PyPI
├── tests/                                  # Тесты
├── docs/                                   # Документация
├── examples/                               # Примеры
├── old/                                    # Резервная копия старого функционала
├── setup.py                                # Конфигурация пакета
├── pyproject.toml                          # Современная конфигурация
├── requirements.txt                        # Зависимости
├── requirements-dev.txt                    # Зависимости для разработки
└── README.md                               # Эта документация
```

## 📦 Установка для разработки

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# Установка в режиме разработки
pip install -e ".[dev]"

# Или установка зависимостей вручную
pip install -r requirements-dev.txt
```

## 🛠️ Ручной запуск без pip

Если вы хотите запустить генератор без установки через pip, используйте прямые скрипты:

### Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# Установите зависимости (если нужно)
pip install -r requirements.txt
```

### Запуск через Python скрипты

```bash
# Основной генератор
python scripts/generate.py

# Или с параметрами
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"

# Анализ контрактов
python scripts/analyze.py --action stats

# Тестирование
python scripts/test.py
```

### Запуск через модули напрямую

```bash
# Запуск основного модуля
python -m src.core.launcher

# Или с параметрами
python -m src.core.launcher --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

### Запуск отдельных компонентов

```bash
# Только генератор метаданных
python -c "
from src.core.metadata_generator import MetadataGenerator
generator = MetadataGenerator('output_dir')
generator.generate('path/to/report.txt')
"

# Только генератор форм
python -c "
from src.core.form_generator import FormGenerator
generator = FormGenerator('output_dir')
generator.generate('path/to/conf_files')
"
```

## 📁 Поддерживаемые типы объектов 1С

### Основные объекты
- **Справочники** - справочные данные
- **Документы** - документооборот
- **Отчеты** - отчетные формы
- **Обработки** - обработки данных

### Регистры
- **РегистрыСведений** - регистры сведений
- **РегистрыНакопления** - регистры накопления
- **РегистрыБухгалтерии** - регистры бухгалтерии
- **РегистрыРасчета** - регистры расчета

### Планы
- **ПланыВидовХарактеристик** - планы видов характеристик
- **ПланыОбмена** - планы обмена
- **ПланыСчетов** - планы счетов
- **ПланыВидовРасчета** - планы видов расчета

### Общие объекты
- **Перечисления** - перечисления
- **ОбщиеМодули** - общие модули
- **ОбщиеКартинки** - общие картинки
- **ОбщиеКоманды** - общие команды

### Сервисы
- **HTTPСервисы** - HTTP сервисы
- **WebСервисы** - Web сервисы
- **XDTOПакеты** - XDTO пакеты

## 📊 Примеры выходных данных

### Контракт метаданных
```json
{
  "type": "Справочник",
  "name": "Номенклатура",
  "comment": "Номенклатура товаров и услуг",
  "properties": [
    {
      "name": "Код",
      "type": "Строка",
      "length": 9,
      "comment": "Код номенклатуры"
    },
    {
      "name": "Наименование",
      "type": "Строка",
      "length": 150,
      "comment": "Наименование номенклатуры"
    }
  ],
  "search_info": {
    "type": "Справочник",
    "category": "ОсновныеОбъекты",
    "full_name": "Справочник_Номенклатура",
    "search_keywords": ["Справочник", "Номенклатура", "товары", "услуги"],
    "object_short_name": "Номенклатура"
  }
}
```

### Контракт формы
```json
{
  "form_type": "ФормаЭлемента",
  "object_name": "Справочник.Номенклатура",
  "form_name": "ФормаЭлементаФорма",
  "controls": [
    {
      "name": "Код",
      "type": "Поле",
      "data_path": "Объект.Код",
      "title": "Код"
    },
    {
      "name": "Наименование",
      "type": "Поле",
      "data_path": "Объект.Наименование",
      "title": "Наименование"
    }
  ]
}
```

## 🔧 Конфигурация

### Переменные окружения
- `ONEC_DEBUG` - включить отладочный режим
- `ONEC_LOG_LEVEL` - уровень логирования (INFO, WARNING, ERROR)

### Параметры командной строки
- `--auto` - автоматический режим
- `--conf-dir` - директория конфигурации
- `--report-path` - путь к отчету
- `--output-dir` - выходная директория
- `--skip-metadata` - пропустить метаданные
- `--skip-forms` - пропустить формы
- `--skip-modules` - пропустить модули

## 📚 Документация

- [📖 Полная документация](docs/README.md)
- [🚀 Руководство по использованию](docs/USAGE.md)
- [📋 Примеры использования](docs/EXAMPLES.md)
- [🔧 API документация](docs/API.md)
- [🛠️ Руководство разработчика](docs/DEVELOPMENT.md)
- [📦 Руководство по публикации](PUBLISH_GUIDE.md)

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src

# Запуск конкретного теста
pytest tests/test_launcher.py::test_main_function

# Запуск с подробным выводом
pytest -v
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

- **Issues**: [GitHub Issues](https://github.com/onec-contract-generator/onec-contract-generator/issues)
- **Email**: support@onec-contract-generator.dev
- **Документация**: [Полная документация](docs/README.md)

## 📈 Статистика проекта

- **Версия**: 2.2.0
- **Python**: 3.7+
- **Лицензия**: MIT
- **Статус**: Активная разработка
- **PyPI**: [onec-contract-generator](https://pypi.org/project/onec-contract-generator/)

---

**Создано с ❤️ для сообщества 1С:Предприятие** 