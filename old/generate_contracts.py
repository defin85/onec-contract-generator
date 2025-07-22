"""
Скрипт для парсинга текстового отчета по конфигурации 1С и создания "контрактов метаданных".

Назначение:
Этот скрипт преобразует неструктурированный текстовый отчет, выгруженный из конфигуратора 1С, 
в набор структурированных JSON-файлов. Эти файлы, называемые "контрактами", описывают
структуру каждого объекта метаданных (справочников, документов и т.д.), включая их 
реквизиты, табличные части и типы данных.

Цель создания таких контрактов — предоставить AI-ассистенту (например, Gemini) 
структурированную и машиночитаемую информацию о метаданных конфигурации. Это позволяет 
ассистенту выполнять глубокий семантический анализ, связывая код из модулей (`src/`) 
с его архитектурным описанием (`metadata_contracts/`).

Принцип работы:
1.  **Очистка:** Перед каждым запуском скрипт полностью очищает целевую директорию, 
    чтобы гарантировать отсутствие устаревших контрактов.
2.  **Чтение отчета:** Скрипт автоматически определяет кодировку файла отчета 
    (пробует UTF-16, затем UTF-8-SIG).
3.  **Парсинг:** Он построчно анализирует отчет, находя "корневые" объекты 
    (например, `Справочники.Контрагенты`) и их дочерние элементы (реквизиты, 
    табличные части).
4.  **Извлечение типов:** Особое внимание уделяется корректному извлечению типов данных, 
    включая сложные многострочные (составные) типы.
5.  **Создание контрактов:** Для каждого найденного объекта метаданных создается 
    JSON-файл (`Контрагенты.json`) в соответствующей директории типа объекта
    (например, `metadata_contracts/Справочники/`).

Использование:
Скрипт запускается из командной строки с двумя аргументами:
- `report_path`: (Обязательный) Путь к текстовому файлу отчета.
- `--output-dir`: (Необязательный) Путь к директории для сохранения контрактов. 
                  По умолчанию используется `metadata_contracts`.

Пример запуска:
`python generate_contracts.py "C:\\YourProject\\conf_reports\\FullReport.txt" --output-dir "my_contracts"`
"""

import os
import argparse
import shutil
import json
import re

# Список корневых объектов, которые мы ищем в отчете
ALLOWED_ROOT_TYPES = [
    "Справочники", "Документы", "Константы", "ОбщиеФормы", "Отчеты",
    "Обработки", "РегистрыСведений", "РегистрыНакопления",
    "ПланыВидовХарактеристик", "ПланыОбмена", "БизнесПроцессы", "Задачи"
]

def clear_directory(directory_path):
    """Полностью очищает указанную директорию, если она существует."""
    if os.path.exists(directory_path):
        print(f"Очистка директории: {directory_path}")
        shutil.rmtree(directory_path)
    os.makedirs(directory_path, exist_ok=True)

def save_contract(current_object, output_dir):
    """Сохраняет накопленный контракт в JSON файл."""
    if not current_object:
        return

    object_type = current_object['type']
    object_name = current_object['object_name']
    
    contract_dir = os.path.join(output_dir, object_type)
    os.makedirs(contract_dir, exist_ok=True)
    
    contract_path = os.path.join(contract_dir, f"{object_name}.json")
    
    print(f"Сохраняю контракт: {contract_path}")
    with open(contract_path, 'w', encoding='utf-8') as cf:
        json.dump(current_object['data'], cf, ensure_ascii=False, indent=4)

def main(report_path, output_dir):
    """Основная функция для парсинга отчета и создания контрактов."""
    
    # 1. Очистка целевой директории
    clear_directory(output_dir)

    # 2. Чтение файла отчета
    if not os.path.exists(report_path):
        print(f"Ошибка: Файл отчета не найден по пути: {report_path}")
        return

    lines = None
    try:
        with open(report_path, 'r', encoding='utf-16') as f:
            lines = f.readlines()
        print("Файл успешно прочитан в кодировке: UTF-16")
    except UnicodeError:
        try:
            with open(report_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            print("Файл успешно прочитан в кодировке: UTF-8-SIG")
        except UnicodeError as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось определить кодировку файла. {e}")
            return
            
    if not lines:
        print("Файл пуст или не удалось прочитать строки.")
        return

    # 3. Парсинг и создание контрактов
    current_object = None
    last_typed_element = None # Ссылка на последний элемент, которому можно присвоить тип
    print(f"Начинаю парсинг отчета: {report_path}")

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        trimmed_line = line.strip()

        # Обнаружение нового элемента метаданных
        if trimmed_line.startswith("-"):
            last_element_line = trimmed_line[1:].strip()
            parts = last_element_line.split('.')
            
            # Проверка, является ли строка определением корневого объекта
            is_valid_root = len(parts) == 2 and parts[0] in ALLOWED_ROOT_TYPES

            if is_valid_root:
                # Сохраняем предыдущий объект
                save_contract(current_object, output_dir)
                
                # Начинаем новый объект
                current_object = {
                    'name': last_element_line,
                    'type': parts[0],
                    'object_name': parts[1],
                    'data': {
                        "name": last_element_line,
                        "type": parts[0],
                        "attributes": [],
                        "tabular_sections": {}
                    }
                }
                last_typed_element = None
                print(f"Найден новый корневой объект: {current_object['name']}")
            
            # Обработка дочерних элементов (реквизитов, таб. частей)
            elif current_object and last_element_line.startswith(current_object['name']):
                child_parts = last_element_line.replace(current_object['name'] + '.', '').split('.')
                
                if len(child_parts) == 2 and child_parts[0] == "Реквизиты":
                    attr = {"name": child_parts[1], "type": ""}
                    current_object['data']['attributes'].append(attr)
                    last_typed_element = attr

                elif len(child_parts) == 2 and child_parts[0] == "ТабличныеЧасти":
                    ts_name = child_parts[1]
                    current_object['data']['tabular_sections'][ts_name] = {
                        "name": ts_name,
                        "attributes": []
                    }
                    last_typed_element = None # Сама ТЧ типа не имеет

                elif len(child_parts) == 4 and child_parts[0] == "ТабличныеЧасти" and child_parts[2] == "Реквизиты":
                    ts_name = child_parts[1]
                    col_name = child_parts[3]
                    if ts_name in current_object['data']['tabular_sections']:
                        col_attr = {"name": col_name, "type": ""}
                        current_object['data']['tabular_sections'][ts_name]['attributes'].append(col_attr)
                        last_typed_element = col_attr

        # Обработка поля "Комментарий"
        elif current_object and trimmed_line.startswith("Комментарий:"):
            comment_text = ""
            try:
                comment_text = trimmed_line.split(":", 1)[1].strip().strip('"')
            except IndexError:
                continue

            if not comment_text:
                continue

            # Определяем, к какому элементу относится комментарий
            target_element = last_typed_element
            if target_element is None:
                target_element = current_object['data']
            
            # Убеждаемся, что работаем со словарем
            if isinstance(target_element, dict):
                target_element['comment'] = comment_text
                
                tasks = re.findall(r'\b\d{5,}\b', comment_text)
                if tasks:
                    # Гарантируем, что 'tasks' существует и является списком
                    if 'tasks' not in target_element or not isinstance(target_element['tasks'], list):
                        target_element['tasks'] = []
                    
                    # Добавляем только уникальные номера задач
                    for task in tasks:
                        if task not in target_element['tasks']:
                            target_element['tasks'].append(task)

        # Обработка поля "Тип:" с поддержкой составных типов
        elif current_object and trimmed_line.startswith("Тип:"):
            type_parts = []
            type_line_indent = len(line) - len(line.lstrip())
            
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_line_indent = len(next_line) - len(next_line.lstrip())
                
                if next_line.strip() and next_line_indent > type_line_indent:
                    part = next_line.strip().strip('",')
                    type_parts.append(part)
                    j += 1
                else:
                    break
            
            if type_parts and last_typed_element:
                full_type = ", ".join(type_parts)
                last_typed_element['type'] = full_type

    # Сохраняем последний накопленный контракт
    save_contract(current_object, output_dir)

    print("\nГенерация контрактов завершена.")
    print(f"Созданные файлы-контракты можно найти в директории '{output_dir}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Генерация контрактов метаданных из отчета по конфигурации 1С.",
        formatter_class=argparse.RawTextHelpFormatter # Для корректного отображения docstring
    )
    parser.add_argument("report_path", help="Путь к текстовому файлу отчета по конфигурации.")
    parser.add_argument("--output-dir", default="metadata_contracts", help="Папка для сохранения сгенерированных контрактов.")
    
    args = parser.parse_args()
    main(args.report_path, args.output_dir)