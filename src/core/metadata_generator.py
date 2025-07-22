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
    "Справочники", "Документы", "Константы", "ОбщиеФормы", "Отчеты",
    "Обработки", "РегистрыСведений", "РегистрыНакопления",
    "ПланыВидовХарактеристик", "ПланыОбмена", "БизнесПроцессы", "Задачи"
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
            print(f"  🧹 Очищаю целевую папку: {self.output_dir}")
            try:
                # Удаляем все файлы .json в папке и подпапках
                for json_file in self.output_dir.rglob("*.json"):
                    json_file.unlink()
                self.log("info", f"Очищена папка: {self.output_dir}")
            except Exception as e:
                self.log("error", f"Ошибка при очистке папки: {e}")
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log("info", f"Создана папка: {self.output_dir}")

    def parse_report(self) -> Dict[str, Any]:
        """Парсит текстовый отчет конфигурации и извлекает структуру метаданных."""
        print(f"  📖 Читаю отчет: {self.report_path}")
        
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            try:
                with open(self.report_path, 'r', encoding='cp1251') as f:
                    content = f.read()
            except Exception as e:
                self.log("error", f"Не удалось прочитать файл отчета: {e}")
                return {}
        
        lines = content.split('\n')
        self.log("info", f"Прочитано строк: {len(lines)}")
        
        # Структура для хранения объектов
        objects = {}
        current_object = None
        current_path = []
        
        for i, line in enumerate(lines):
            trimmed_line = line.strip()
            if not trimmed_line:
                continue
                
            # Определяем уровень вложенности
            indent_level = len(line) - len(line.lstrip())
            
            # Если это корневой объект
            if indent_level == 0 and any(trimmed_line.startswith(f"- {root_type}.") for root_type in ALLOWED_ROOT_TYPES):
                # Извлекаем имя объекта
                object_name = trimmed_line[2:]  # Убираем "- "
                current_object = object_name
                current_path = [object_name]
                
                # Инициализируем структуру объекта
                objects[object_name] = {
                    "name": object_name,
                    "type": self._extract_object_type(object_name),
                    "attributes": [],
                    "tabular_sections": [],
                    "comment": ""
                }
                
                self.log("info", f"Найден объект: {object_name}")
                
            # Если это вложенный элемент
            elif current_object and indent_level > 0:
                # Убираем отступы и дефис
                clean_line = trimmed_line.lstrip('- ').strip()
                
                if clean_line.startswith("Комментарий:"):
                    comment = clean_line[12:].strip().strip('"')
                    if current_object in objects:
                        objects[current_object]["comment"] = comment
                        
                # Обработка поля "Тип:" с поддержкой составных типов
                elif clean_line.startswith("Тип:"):
                    type_value = clean_line[4:].strip()
                    if type_value and current_object in objects:
                        # Ищем последний добавленный атрибут
                        if objects[current_object]["attributes"]:
                            last_attr = objects[current_object]["attributes"][-1]
                            last_attr["type"] = type_value
                            self.log("info", f"Установлен тип для {last_attr['name']}: {type_value}")
                
                # Обработка реквизитов
                elif "." in clean_line and not clean_line.startswith("Комментарий:") and not clean_line.startswith("Тип:"):
                    # Извлекаем имя реквизита
                    attr_name = clean_line.split('.')[-1]
                    
                    # Определяем, это реквизит или табличная часть
                    if "ТабличныеЧасти" in clean_line:
                        # Это табличная часть
                        tab_section = {
                            "name": attr_name,
                            "type": "ТабличнаяЧасть",
                            "attributes": []
                        }
                        objects[current_object]["tabular_sections"].append(tab_section)
                        self.log("info", f"Добавлена табличная часть: {attr_name}")
                    else:
                        # Это обычный реквизит
                        attr = {
                            "name": attr_name,
                            "type": "Неопределено",
                            "path": clean_line
                        }
                        objects[current_object]["attributes"].append(attr)
                        self.log("info", f"Добавлен реквизит: {attr_name}")
        
        self.log("summary", f"Обработано объектов: {len(objects)}")
        return objects

    def _extract_object_type(self, object_name: str) -> str:
        """Извлекает тип объекта из его имени."""
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
        else:
            return "Неопределено"

    def generate_contract(self, object_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует контракт для одного объекта метаданных."""
        contract = {
            "metadata_type": "Object",
            "name": object_data["name"],
            "type": object_data["type"],
            "comment": object_data["comment"],
            "structure": {
                "attributes_count": len(object_data["attributes"]),
                "tabular_sections_count": len(object_data["tabular_sections"]),
                "attributes": object_data["attributes"],
                "tabular_sections": object_data["tabular_sections"]
            },
            "generated_at": str(Path().cwd()),
            "source": "Text Report"
        }
        
        return contract

    def save_contract(self, contract: Dict[str, Any], object_name: str):
        """Сохраняет контракт объекта в JSON файл."""
        try:
            # Определяем папку для сохранения
            object_type = contract["type"]
            if object_type == "Справочник":
                folder = "Справочники"
            elif object_type == "Документ":
                folder = "Документы"
            elif object_type == "Отчет":
                folder = "Отчеты"
            elif object_type == "Обработка":
                folder = "Обработки"
            elif object_type == "Константа":
                folder = "Константы"
            else:
                folder = "Прочее"
            
            # Создаем папку
            output_folder = self.output_dir / folder
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Извлекаем имя объекта без префикса типа
            object_short_name = object_name.split('.')[-1]
            
            # Сохраняем файл
            output_file = output_folder / f"{object_short_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(contract, f, ensure_ascii=False, indent=2)
            
            self.log("success", f"Создан контракт: {object_short_name}")
            
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