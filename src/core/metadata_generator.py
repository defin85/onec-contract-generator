"""
Генератор контрактов метаданных объектов 1С.

Назначение:
Генерирует JSON-контракты для объектов метаданных (справочники, документы и т.д.)
из текстового отчета конфигурации.
"""

import os
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Список корневых объектов, которые мы ищем в отчете
ALLOWED_ROOT_TYPES = [
    # Основные типы объектов
    "Справочники", "Документы", "Константы", "ОбщиеФормы", "Отчеты",
    "Обработки", "РегистрыСведений", "РегистрыНакопления",
    "ПланыВидовХарактеристик", "ПланыОбмена", "БизнесПроцессы", "Задачи",
    
    # Дополнительные типы из реального отчета
    "Конфигурации", "Языки", "Подсистемы", "Роли", "ПланыСчетов",
    "РегистрыБухгалтерии", "РегистрыРасчета", "ПланыВидовРасчета",
    "ПланыВидовСчетов", "ПланыВидовНоменклатуры", "ПланыВидовСвойств",
    "ПланыВидовСчетовБухгалтерии", "ПланыВидовСчетовНалоговогоУчета",
    
    # Типы из структуры папок конфигурации (исправленные названия)
    "Перечисления", "ОбщиеМодули", "HTTPСервисы", "WebСервисы", 
    "XDTOПакеты", "Стили", "ЭлементыСтиля", "ХранилищаНастроек",
    "ПараметрыСеанса", "РегламентныеЗадания", "ЖурналыДокументов",
    "ОпределяемыеТипы", "ОбщиеКартинки", "ОбщиеКоманды", "ОбщиеРеквизиты",
    "ГруппыКоманд", "ПланыВидовХарактеристик", "Боты", "ПодпискиНаСобытия",
    "ФункциональныеОпции", "ПараметрыФункциональныхОпций", "КритерииОтбора",
    
    # Дополнительные типы, которые могут быть в отчете
    "ОбщиеШаблоны", "Расширения"
]

class MetadataGenerator:
    """Генератор контрактов метаданных объектов."""
    
    def __init__(self, report_path: str, output_dir: str):
        self.report_path = Path(report_path)
        self.output_dir = Path(output_dir)
        self.logs = defaultdict(list)  # Группировка логов по категориям
        
    def log(self, category: str, message: str):
        """Добавляет сообщение в лог с группировкой по категориям."""
        self.logs[category].append(message)
        
    def print_logs(self):
        """Выводит сгруппированные логи."""
        if not self.logs:
            return
            
        print("\n📋 Сводка по генерации контрактов метаданных:")
        print("=" * 50)
        
        for category, messages in self.logs.items():
            if messages:
                print(f"\n🔍 {category} ({len(messages)}):")
                for msg in messages[:5]:  # Показываем только первые 5 сообщений
                    print(f"  • {msg}")
                if len(messages) > 5:
                    print(f"  ... и еще {len(messages) - 5} сообщений")
        
        print("=" * 50)

    def clean_output_directory(self):
        """Очищает целевую папку от старых файлов контрактов метаданных."""
        if self.output_dir.exists():
            self.log("info", f"Очищаю целевую папку: {self.output_dir}")
            try:
                # Удаляем только файлы .json, сохраняя структуру папок
                deleted_files = 0
                for json_file in self.output_dir.rglob("*.json"):
                    json_file.unlink()
                    deleted_files += 1
                
                self.log("success", f"Очищена папка: удалено {deleted_files} файлов")
            except Exception as e:
                self.log("error", f"Ошибка при очистке папки: {e}")
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log("info", f"Создана папка: {self.output_dir}")

    def parse_report(self) -> Dict[str, Any]:
        """Парсит текстовый отчет конфигурации и извлекает структуру метаданных."""
        self.log("info", f"Читаю отчет: {self.report_path}")
        
        # Читаем файл с правильной кодировкой
        lines = None
        try:
            with open(self.report_path, 'r', encoding='utf-16') as f:
                lines = f.readlines()
            self.log("info", "Файл успешно прочитан в кодировке: UTF-16")
        except UnicodeError:
            try:
                with open(self.report_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                self.log("info", "Файл успешно прочитан в кодировке: UTF-8-SIG")
            except UnicodeError:
                try:
                    with open(self.report_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    self.log("info", "Файл успешно прочитан в кодировке: UTF-8")
                except UnicodeError:
                    try:
                        with open(self.report_path, 'r', encoding='cp1251') as f:
                            lines = f.readlines()
                        self.log("info", "Файл успешно прочитан в кодировке: CP1251")
                    except Exception as e:
                        self.log("error", f"Не удалось прочитать файл отчета: {e}")
                        return {}
        
        if not lines:
            self.log("error", "Файл пуст или не удалось прочитать строки")
            return {}
        
        self.log("info", f"Прочитано строк: {len(lines)}")
        
        # Структура для хранения объектов
        objects = {}
        current_object = None
        last_typed_element = None
        processed_lines = 0
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            processed_lines += 1
            trimmed_line = line.strip()
            
            # Обнаружение нового элемента метаданных
            if trimmed_line.startswith("-"):
                last_element_line = trimmed_line[1:].strip()
                parts = last_element_line.split('.')
                
                # Проверка, является ли строка определением корневого объекта
                is_valid_root = len(parts) == 2 and parts[0] in ALLOWED_ROOT_TYPES
                
                # Отладочная информация
                if len(parts) == 2 and parts[0] in ALLOWED_ROOT_TYPES:
                    self.log("info", f"Найден корневой объект: {last_element_line}")
                elif len(parts) == 2:
                    self.log("warning", f"Неизвестный тип объекта: {parts[0]} в строке {last_element_line}")
                    # Добавляем информацию для анализа
                    if parts[0] not in [msg.split(': ')[1].split(' ')[0] for msg in self.logs.get('warning', [])]:
                        self.log("info", f"НОВЫЙ НЕИЗВЕСТНЫЙ ТИП: {parts[0]} - добавьте в ALLOWED_ROOT_TYPES")
                
                if is_valid_root:
                    # Начинаем новый объект
                    object_name = last_element_line
                    current_object = {
                        "name": object_name,
                        "type": self._extract_object_type(object_name),  # Используем правильный метод
                        "attributes": [],
                        "tabular_sections": {},
                        "comment": ""
                    }
                    objects[object_name] = current_object
                    last_typed_element = None
                    self.log("info", f"Найден корневой объект: {object_name}")
                
                # Обработка дочерних элементов (реквизитов, таб. частей)
                elif current_object and last_element_line.startswith(current_object['name']):
                    child_parts = last_element_line.replace(current_object['name'] + '.', '').split('.')
                    
                    if len(child_parts) == 2 and child_parts[0] == "Реквизиты":
                        attr = {"name": child_parts[1], "type": "Неопределено", "path": last_element_line}
                        current_object['attributes'].append(attr)
                        last_typed_element = attr
                        self.log("info", f"Добавлен реквизит: {child_parts[1]}")
                    
                    elif len(child_parts) == 2 and child_parts[0] == "ТабличныеЧасти":
                        ts_name = child_parts[1]
                        current_object['tabular_sections'][ts_name] = {
                            "name": ts_name,
                            "type": "ТабличнаяЧасть",
                            "attributes": []
                        }
                        last_typed_element = None
                        self.log("info", f"Добавлена табличная часть: {ts_name}")
                    
                    elif len(child_parts) == 4 and child_parts[0] == "ТабличныеЧасти" and child_parts[2] == "Реквизиты":
                        ts_name = child_parts[1]
                        col_name = child_parts[3]
                        if ts_name in current_object['tabular_sections']:
                            col_attr = {"name": col_name, "type": "Неопределено", "path": last_element_line}
                            current_object['tabular_sections'][ts_name]['attributes'].append(col_attr)
                            last_typed_element = col_attr
                            self.log("info", f"Добавлен реквизит табличной части {ts_name}: {col_name}")
            
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
                    target_element = current_object
                
                # Убеждаемся, что работаем со словарем
                if isinstance(target_element, dict):
                    target_element['comment'] = comment_text
            
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
                    self.log("info", f"Установлен тип для {last_typed_element['name']}: {full_type}")
        
        self.log("summary", f"Обработано объектов: {len(objects)}")
        self.log("info", f"Обработано строк: {processed_lines} из {len(lines)}")
        return objects

    def _extract_object_type(self, object_name: str) -> str:
        """Извлекает тип объекта из его имени."""
        # Основные типы
        if object_name.startswith("Справочники."):
            return "Справочник"
        elif object_name.startswith("Документы."):
            return "Документ"
        elif object_name.startswith("Константы."):
            return "Константа"
        elif object_name.startswith("Отчеты."):
            return "Отчет"
        elif object_name.startswith("Обработки."):
            return "Обработка"
        elif object_name.startswith("РегистрыСведений."):
            return "РегистрСведений"
        elif object_name.startswith("РегистрыНакопления."):
            return "РегистрНакопления"
        elif object_name.startswith("РегистрыБухгалтерии."):
            return "РегистрБухгалтерии"
        elif object_name.startswith("РегистрыРасчета."):
            return "РегистрРасчета"
        
        # Планы
        elif object_name.startswith("ПланыВидовХарактеристик."):
            return "ПланВидовХарактеристик"
        elif object_name.startswith("ПланыОбмена."):
            return "ПланОбмена"
        elif object_name.startswith("ПланыСчетов."):
            return "ПланСчетов"
        elif object_name.startswith("ПланыВидовРасчета."):
            return "ПланВидовРасчета"
        elif object_name.startswith("ПланыВидовСчетов."):
            return "ПланВидовСчетов"
        elif object_name.startswith("ПланыВидовНоменклатуры."):
            return "ПланВидовНоменклатуры"
        elif object_name.startswith("ПланыВидовСвойств."):
            return "ПланВидовСвойств"
        elif object_name.startswith("ПланыВидовСчетовБухгалтерии."):
            return "ПланВидовСчетовБухгалтерии"
        elif object_name.startswith("ПланыВидовСчетовНалоговогоУчета."):
            return "ПланВидовСчетовНалоговогоУчета"
        
        # Другие типы
        elif object_name.startswith("Перечисления."):
            return "Перечисление"
        elif object_name.startswith("ОбщиеМодули."):
            return "ОбщийМодуль"
        elif object_name.startswith("HTTPСервисы."):
            return "HTTPСервис"
        elif object_name.startswith("WebСервисы."):
            return "WebСервис"
        elif object_name.startswith("XDTOПакеты."):
            return "XDTOПакет"
        elif object_name.startswith("Стили."):
            return "Стиль"
        elif object_name.startswith("ЭлементыСтилей."):
            return "ЭлементСтиля"
        elif object_name.startswith("ХранилищаНастроек."):
            return "ХранилищеНастроек"
        elif object_name.startswith("ПараметрыСеанса."):
            return "ПараметрСеанса"
        elif object_name.startswith("РегламентныеЗадания."):
            return "РегламентноеЗадание"
        elif object_name.startswith("ЖурналыДокументов."):
            return "ЖурналДокументов"
        elif object_name.startswith("ОпределяемыеТипы."):
            return "ОпределяемыйТип"
        elif object_name.startswith("ОбщиеКартинки."):
            return "ОбщаяКартинка"
        elif object_name.startswith("ОбщиеКоманды."):
            return "ОбщаяКоманда"
        elif object_name.startswith("ОбщиеРеквизиты."):
            return "ОбщийРеквизит"
        elif object_name.startswith("ГруппыКоманд."):
            return "ГруппаКоманд"
        elif object_name.startswith("Боты."):
            return "Бот"
        elif object_name.startswith("ПодпискиНаСобытия."):
            return "ПодпискаНаСобытие"
        elif object_name.startswith("ФункциональныеОпции."):
            return "ФункциональнаяОпция"
        elif object_name.startswith("ПараметрыФункциональныхОпций."):
            return "ПараметрФункциональнойОпции"
        elif object_name.startswith("КритерииОтбора."):
            return "КритерийОтбора"
        
        # Системные типы
        elif object_name.startswith("Конфигурации."):
            return "Конфигурация"
        elif object_name.startswith("Языки."):
            return "Язык"
        elif object_name.startswith("Подсистемы."):
            return "Подсистема"
        elif object_name.startswith("Роли."):
            return "Роль"
        elif object_name.startswith("БизнесПроцессы."):
            return "БизнесПроцесс"
        elif object_name.startswith("Задачи."):
            return "Задача"
        elif object_name.startswith("ОбщиеШаблоны."):
            return "ОбщийШаблон"
        elif object_name.startswith("Расширения."):
            return "Расширение"
        
        else:
            return "Неопределено"
    
    def _get_category_for_type(self, object_type: str) -> str:
        """Определяет категорию для типа объекта."""
        categories = {
            # Основные объекты
            "Справочник": "ОсновныеОбъекты",
            "Документ": "ОсновныеОбъекты", 
            "Отчет": "ОсновныеОбъекты",
            "Обработка": "ОсновныеОбъекты",
            "Константа": "ОсновныеОбъекты",
            
            # Регистры
            "РегистрСведений": "Регистры",
            "РегистрНакопления": "Регистры",
            "РегистрБухгалтерии": "Регистры",
            "РегистрРасчета": "Регистры",
            
            # Планы
            "ПланВидовХарактеристик": "Планы",
            "ПланОбмена": "Планы",
            "ПланСчетов": "Планы",
            "ПланВидовРасчета": "Планы",
            "ПланВидовСчетов": "Планы",
            "ПланВидовНоменклатуры": "Планы",
            "ПланВидовСвойств": "Планы",
            "ПланВидовСчетовБухгалтерии": "Планы",
            "ПланВидовСчетовНалоговогоУчета": "Планы",
            
            # Общие объекты
            "Перечисление": "ОбщиеОбъекты",
            "ОбщийМодуль": "ОбщиеОбъекты",
            "ОбщаяКартинка": "ОбщиеОбъекты",
            "ОбщаяКоманда": "ОбщиеОбъекты",
            "ОбщийРеквизит": "ОбщиеОбъекты",
            "ОбщийШаблон": "ОбщиеОбъекты",
            
            # Сервисы и интеграция
            "HTTPСервис": "Сервисы",
            "WebСервис": "Сервисы",
            "XDTOПакет": "Сервисы",
            
            # Системные объекты
            "Стиль": "СистемныеОбъекты",
            "ЭлементСтиля": "СистемныеОбъекты",
            "ХранилищеНастроек": "СистемныеОбъекты",
            "ПараметрСеанса": "СистемныеОбъекты",
            "РегламентноеЗадание": "СистемныеОбъекты",
            "ЖурналДокументов": "СистемныеОбъекты",
            "ОпределяемыйТип": "СистемныеОбъекты",
            "ГруппаКоманд": "СистемныеОбъекты",
            "Бот": "СистемныеОбъекты",
            "ПодпискаНаСобытие": "СистемныеОбъекты",
            "ФункциональнаяОпция": "СистемныеОбъекты",
            "ПараметрФункциональнойОпции": "СистемныеОбъекты",
            "КритерийОтбора": "СистемныеОбъекты",
            
            # Конфигурация
            "Конфигурация": "Конфигурация",
            "Язык": "Конфигурация",
            "Подсистема": "Конфигурация",
            "Роль": "Конфигурация",
            "БизнесПроцесс": "Конфигурация",
            "Задача": "Конфигурация",
            "Расширение": "Конфигурация"
        }
        
        return categories.get(object_type, "Прочее")

    def generate_contract(self, object_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует контракт для одного объекта метаданных."""
        # Преобразуем табличные части из словаря в список для совместимости
        tabular_sections_list = []
        for ts_name, ts_data in object_data["tabular_sections"].items():
            tabular_sections_list.append(ts_data)
        
        # Извлекаем имя объекта без префикса типа
        object_short_name = object_data["name"].split('.')[-1]
        
        # Создаем поисковые ключевые слова
        search_keywords = [
            object_data["type"].lower(),
            object_short_name.lower(),
            object_data["name"].lower()
        ]
        
        # Добавляем ключевые слова из комментария
        if object_data.get("comment"):
            comment_words = object_data["comment"].lower().split()
            search_keywords.extend([word for word in comment_words if len(word) > 2])
        
        contract = {
            "metadata_type": "Object",
            "name": object_data["name"],
            "type": object_data["type"],
            "comment": object_data["comment"],
            "structure": {
                "attributes_count": len(object_data["attributes"]),
                "tabular_sections_count": len(object_data["tabular_sections"]),
                "attributes": object_data["attributes"],
                "tabular_sections": tabular_sections_list
            },
            "search_info": {
                "type": object_data["type"],
                "category": self._get_category_for_type(object_data["type"]),
                "full_name": f"{object_data['type']}_{object_short_name}",
                "search_keywords": list(set(search_keywords)),  # Убираем дубликаты
                "object_short_name": object_short_name
            },
            "generated_at": str(Path().cwd()),
            "source": "Text Report"
        }
        
        return contract

    def save_contract(self, contract: Dict[str, Any], object_name: str):
        """Сохраняет контракт объекта в JSON файл."""
        try:
            # Используем полное имя из search_info для названия файла
            full_name = contract["search_info"]["full_name"]
            
            # Сохраняем в плоской структуре (без папок)
            output_file = self.output_dir / f"{full_name}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(contract, f, ensure_ascii=False, indent=2)
            
            self.log("success", f"Создан контракт: {full_name}")
            
        except Exception as e:
            self.log("error", f"Ошибка при сохранении контракта {object_name}: {e}")

    def generate(self) -> bool:
        """Основной метод генерации контрактов метаданных."""
        print("🔄 Генерация контрактов метаданных...")
        
        # Очищаем папку
        self.clean_output_directory()
        
        # Парсим отчет
        objects = self.parse_report()
        if not objects:
            self.log("error", "Не удалось извлечь объекты из отчета")
            self.print_logs()
            return False 
        
        # Генерируем контракты
        success_count = 0
        for object_name, object_data in objects.items():
            try:
                contract = self.generate_contract(object_data)
                self.save_contract(contract, object_name)
                success_count += 1
            except Exception as e:
                self.log("error", f"Ошибка при генерации контракта для {object_name}: {e}")
        
        # Выводим результаты
        self.log("summary", f"Обработано объектов: {len(objects)}, успешно: {success_count}")
        self.print_logs()
        
        return success_count > 0 