# 🔧 Документация для разработчиков

## 🚀 Установка для разработки

### Подготовка окружения

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка в режиме разработки
pip install -e ".[dev]"

# Или установка зависимостей вручную
pip install -r requirements-dev.txt
```

### Проверка установки

```bash
# Проверка импорта
python -c "import core; print('✅ Импорт успешен')"

# Запуск тестов
pytest

# Проверка команд (через pip)
onec-contract-generate --help

# Или ручной запуск
python scripts/generate.py --help
```

## 🏗️ Архитектура системы

### 📁 Структура проекта

```
onec-contract-generator/
├── src/                            # Исходный код
│   ├── core/                       # Основные компоненты
│   │   ├── launcher.py             # 🚀 Единый запускатор системы
│   │   ├── metadata_generator.py   # 📋 Генератор контрактов метаданных
│   │   ├── form_generator.py       # 📝 Генератор контрактов форм
│   │   └── module_generator.py     # 🔧 Генератор контрактов модулей
│   ├── utils/                      # Утилиты (пока не реализованы)
│   └── parsers/                    # Парсеры (пока не реализованы)
├── scripts/                        # Скрипты
│   ├── generate.py                 # Главный скрипт
│   ├── analyze.py                  # Скрипт анализа
│   ├── test.py                     # Скрипт тестирования
│   └── publish.py                  # Скрипт публикации
├── tests/                          # Тесты
├── docs/                           # Документация
├── examples/                       # Примеры
├── setup.py                        # Конфигурация пакета
├── pyproject.toml                  # Современная конфигурация
├── requirements.txt                # Зависимости
├── requirements-dev.txt            # Зависимости для разработки
└── MANIFEST.in                     # Файлы для включения в пакет
```

### 🔄 Поток данных

```
Входные данные → Парсеры → Генераторы → Контракты → Анализ
     ↓              ↓          ↓          ↓         ↓
  XML файлы    → XML Parser → Form Gen → JSON → Validator
  Текстовые    → Text Parser → Metadata Gen → JSON → Analyzer
  отчеты       → BSL Parser → Module Gen → JSON → Reporter
```

## 🎯 Основные компоненты

### 🚀 ContractGeneratorLauncher (`src/core/launcher.py`)

**Назначение**: Единая точка входа в систему

**Основные функции**:
- Парсинг аргументов командной строки
- Координация работы генераторов
- Интерактивный режим
- Обработка ошибок

**Ключевые методы**:
```python
def run_interactive_mode()      # Интерактивный мастер
def run_auto_mode()            # Автоматический режим
def validate_paths()           # Валидация путей
def generate_contracts()       # Координация генерации
```

### 📋 MetadataGenerator (`src/core/metadata_generator.py`)

**Назначение**: Генерация контрактов метаданных из текстовых отчетов

**Основные функции**:
- Парсинг текстовых отчетов конфигурации
- Извлечение структуры объектов
- Генерация JSON контрактов
- Группированное логирование
- Гибридная организация файлов

**Ключевые методы**:
```python
def parse_report()             # Парсинг отчета
def generate_contract()        # Генерация контракта
def save_contract()            # Сохранение контракта
def log()                      # Логирование
def _get_category_for_type()   # Определение категории
def _extract_object_type()     # Извлечение типа объекта
```

**Поддерживаемые типы объектов**:
```python
ALLOWED_ROOT_TYPES = [
    "Конфигурации", "Языки", "Подсистемы", "Роли", "ПланыСчетов",
    "РегистрыБухгалтерии", "РегистрыРасчета", "ПланыВидовРасчета",
    "ПланыВидовСчетов", "ПланыВидовНоменклатуры", "ПланыВидовСвойств",
    "ПланыВидовСчетовБухгалтерии", "ПланыВидовСчетовНалоговогоУчета",
    "Перечисления", "ОбщиеМодули", "HTTPСервисы", "WebСервисы",
    "XDTOПакеты", "Стили", "ЭлементыСтиля", "ХранилищаНастроек",
    "ПараметрыСеанса", "РегламентныеЗадания", "ЖурналыДокументов",
    "ОпределяемыеТипы", "ОбщиеКартинки", "ОбщиеКоманды", "ОбщиеРеквизиты",
    "ГруппыКоманд", "Боты", "ПодпискиНаСобытия", "ФункциональныеОпции",
    "ПараметрыФункциональныхОпций", "КритерииОтбора", "ОбщиеШаблоны",
    "Расширения", "Справочники", "Документы", "Отчеты", "Обработки",
    "РегистрыСведений", "РегистрыНакопления", "ПланыВидовХарактерик",
    "ПланыОбмена"
]
```

### 📝 FormGenerator (`src/core/form_generator.py`)

**Назначение**: Генерация контрактов форм из XML файлов

**Основные функции**:
- Парсинг XML файлов форм
- Извлечение свойств форм
- Генерация структурированных контрактов
- Обработка ошибок парсинга

**Ключевые методы**:
```python
def find_form_files()          # Поиск файлов форм
def parse_form_file()          # Парсинг XML
def generate_form_contract()   # Генерация контракта
def process_form_file()        # Обработка файла
```

### 🔧 ModuleGenerator (`src/core/module_generator.py`)

**Назначение**: Генерация контрактов модулей из XML файлов (заглушка)

**Основные функции**:
- Парсинг XML файлов модулей
- Извлечение функций и процедур
- Генерация контрактов модулей
- Обработка различных типов модулей

## 📊 Система логирования

### 🏷️ Категории логов

```python
LOG_CATEGORIES = {
    "info": "Информационные сообщения",
    "success": "Успешно обработанные файлы",
    "warning": "Предупреждения",
    "error": "Ошибки обработки",
    "summary": "Сводки по результатам"
}
```

### 📝 Пример использования

```python
from core.metadata_generator import MetadataGenerator

generator = MetadataGenerator("report.txt", "output")

# Добавление логов
generator.log("info", "Начало обработки файла")
generator.log("success", "Файл обработан успешно")
generator.log("warning", "Неизвестный тип объекта")
generator.log("error", "Ошибка парсинга XML")
generator.log("summary", "Обработано 100 объектов")

# Вывод сгруппированных логов
generator.print_logs()
```

## 🚀 Запуск и разработка

### Ручной запуск без pip

Для разработки и отладки удобно использовать прямые скрипты:

```bash
# Основной генератор
python scripts/generate.py

# Или через модули напрямую
python -m src.core.launcher

# С параметрами
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"

# Анализ контрактов
python scripts/analyze.py --action stats

# Тестирование
python scripts/test.py
```

### Отладка отдельных компонентов

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

# Только генератор модулей
python -c "
from src.core.module_generator import ModuleGenerator
generator = ModuleGenerator('output_dir')
generator.generate('path/to/conf_files')
"
```

### Отладочный режим

```bash
# Включение отладочного режима
export ONEC_DEBUG=1
python scripts/generate.py

# Или через переменную окружения
set ONEC_DEBUG=1  # Windows
python scripts/generate.py
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# Или через скрипт
python scripts/test.py

# С покрытием
pytest --cov=src

# Конкретный тест
pytest tests/test_launcher.py::test_main_function

# С подробным выводом
pytest -v

# Только быстрые тесты
pytest -m "not slow"
```

### Структура тестов

```
tests/
├── test_launcher.py           # Тесты запускатора
├── test_metadata_generator.py # Тесты генератора метаданных
├── test_form_generator.py     # Тесты генератора форм
└── test_module_generator.py   # Тесты генератора модулей
```

### Написание тестов

```python
import pytest
from core.metadata_generator import MetadataGenerator

def test_metadata_generator_creation():
    """Тест создания генератора метаданных"""
    generator = MetadataGenerator("test_report.txt", "test_output")
    assert generator.report_path == "test_report.txt"
    assert generator.output_dir == "test_output"

def test_parse_report():
    """Тест парсинга отчета"""
    generator = MetadataGenerator("test_report.txt", "test_output")
    # Создаем тестовый файл
    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write("Справочники.Номенклатура\n")
        f.write("  Реквизиты\n")
        f.write("    Код (Строка, 9)\n")
    
    result = generator.parse_report()
    assert "Справочники.Номенклатура" in result
```

## 🔧 Конфигурация пакета

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="onec-contract-generator",
    version="2.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "onec-contract-generate=core.launcher:main",
            "onec-contract-analyze=scripts.analyze:main",
            "onec-contract-test=scripts.test:main",
        ],
    },
    # ... остальные параметры
)
```

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "onec-contract-generator"
dynamic = ["version"]
description = "Autonomous system for generating structured JSON contracts from 1C:Enterprise configurations"
# ... остальные параметры
```

### MANIFEST.in

```
include README.md
include requirements.txt
include requirements-dev.txt
include LICENSE
include CHANGELOG.md
include pyproject.toml
recursive-include docs *.md
recursive-include examples *
recursive-include scripts *.py
recursive-include tests *.py
```

## 📦 Публикация на PyPI

### Подготовка к публикации

```bash
# Установка инструментов
pip install build twine

# Проверка конфигурации
python -c "import build; print('✅ build установлен')"
twine --version

# Очистка предыдущих сборок
rm -rf dist/ build/ *.egg-info/
```

### Сборка пакета

```bash
# Сборка
python -m build

# Проверка пакета
twine check dist/*

# Тестовая публикация
twine upload --repository testpypi dist/*

# Продакшн публикация
twine upload dist/*
```

### Автоматизация

```bash
# Использование скрипта публикации
python scripts/publish.py
```

## 🔍 Отладка

### Переменные окружения

```bash
# Отладочный режим
export ONEC_DEBUG=1

# Уровень логирования
export ONEC_LOG_LEVEL=INFO

# Запуск с отладкой
onec-contract-generate --auto \
  --conf-dir "test_conf_files" \
  --report-path "test_report.txt"
```

### Логирование в коде

```python
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Отладочное сообщение")
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
```

## 🚀 Разработка новых функций

### Добавление нового типа объекта

1. **Обновите `ALLOWED_ROOT_TYPES`** в `metadata_generator.py`:
```python
ALLOWED_ROOT_TYPES.append("НовыйТипОбъекта")
```

2. **Добавьте категорию** в `_get_category_for_type()`:
```python
def _get_category_for_type(self, object_type: str) -> str:
    if object_type in ["НовыйТипОбъекта"]:
        return "НоваяКатегория"
    # ... остальные условия
```

3. **Добавьте маппинг** в `_extract_object_type()`:
```python
def _extract_object_type(self, plural_name: str) -> str:
    type_mapping = {
        "НовыеТипыОбъектов": "НовыйТипОбъекта",
        # ... остальные маппинги
    }
    return type_mapping.get(plural_name, plural_name)
```

4. **Напишите тесты**:
```python
def test_new_object_type():
    generator = MetadataGenerator("test.txt", "output")
    category = generator._get_category_for_type("НовыйТипОбъекта")
    assert category == "НоваяКатегория"
```

### Добавление нового генератора

1. **Создайте новый файл** в `src/core/`:
```python
# new_generator.py
class NewGenerator:
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        self.logs = {"info": [], "success": [], "warning": [], "error": [], "summary": []}
    
    def generate(self) -> bool:
        # Реализация генерации
        pass
    
    def log(self, category: str, message: str):
        if category in self.logs:
            self.logs[category].append(message)
```

2. **Интегрируйте в запускатор**:
```python
# В launcher.py
from core.new_generator import NewGenerator

def generate_contracts(self):
    # ... существующий код ...
    
    if not self.skip_new:
        self.log("info", "Генерация новых контрактов...")
        new_gen = NewGenerator(self.input_path, self.output_dir)
        new_success = new_gen.generate()
        # ... обработка результатов
```

3. **Добавьте тесты**:
```python
# test_new_generator.py
def test_new_generator():
    generator = NewGenerator("test_input", "test_output")
    success = generator.generate()
    assert success == True
```

## 📚 Лучшие практики

### Код-стайл

- Используйте **типизацию** для всех функций
- Добавляйте **docstrings** для всех методов
- Следуйте **PEP 8** для форматирования
- Используйте **f-строки** вместо `.format()`

### Обработка ошибок

```python
try:
    # Потенциально опасный код
    result = process_file(file_path)
except FileNotFoundError:
    self.log("error", f"Файл не найден: {file_path}")
    return False
except Exception as e:
    self.log("error", f"Неожиданная ошибка: {e}")
    return False
```

### Логирование

```python
def process_data(self, data):
    self.log("info", f"Начало обработки {len(data)} элементов")
    
    for item in data:
        try:
            result = self.process_item(item)
            self.log("success", f"Обработан элемент: {item}")
        except Exception as e:
            self.log("warning", f"Ошибка обработки {item}: {e}")
    
    self.log("summary", f"Обработано элементов: {len(data)}")
```

## 🔗 Связанные документы

- [📖 Руководство по использованию](USAGE.md)
- [📋 Примеры использования](EXAMPLES.md)
- [🔧 API документация](API.md)
- [📦 Руководство по публикации](../PUBLISH_GUIDE.md) 