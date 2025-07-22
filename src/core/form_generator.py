"""
Генератор контрактов форм 1С.

Назначение:
Генерирует JSON-контракты для форм из XML-описаний и BSL-модулей.
"""

import os
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

class FormGenerator:
    """Генератор контрактов форм."""
    
    def __init__(self, conf_dir: str, output_dir: str):
        self.conf_dir = Path(conf_dir)
        self.output_dir = Path(output_dir)
        self.logs = defaultdict(list)  # Группировка логов по категориям
        
    def log(self, category: str, message: str):
        """Добавляет сообщение в лог с группировкой по категориям."""
        self.logs[category].append(message)
        
    def print_logs(self):
        """Выводит сгруппированные логи."""
        if not self.logs:
            return
            
        print("\n📋 Сводка по генерации контрактов форм:")
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
        """Очищает целевую папку от старых файлов контрактов форм."""
        if self.output_dir.exists():
            print(f"  🧹 Очищаю целевую папку: {self.output_dir}")
            try:
                # Удаляем все файлы .json в папке
                for json_file in self.output_dir.glob("*.json"):
                    json_file.unlink()
                self.log("info", f"Очищена папка: {self.output_dir}")
            except Exception as e:
                self.log("error", f"Ошибка при очистке папки: {e}")
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log("info", f"Создана папка: {self.output_dir}")

    def find_form_files(self) -> List[Path]:
        """Находит все XML файлы форм в конфигурации."""
        form_files = []
        
        # Ищем формы в разных папках
        search_patterns = [
            "**/Forms/*.xml",
            "**/Forms/*/*.xml",
            "**/Form/*.xml"
        ]
        
        for pattern in search_patterns:
            try:
                files = list(self.conf_dir.glob(pattern))
                form_files.extend(files)
                self.log("info", f"Найдено {len(files)} файлов форм по паттерну: {pattern}")
            except Exception as e:
                self.log("error", f"Ошибка при поиске по паттерну {pattern}: {e}")
        
        # Убираем дубликаты
        unique_files = list(set(form_files))
        self.log("info", f"Всего найдено уникальных файлов форм: {len(unique_files)}")
        
        return unique_files

    def parse_form_xml(self, xml_path: Path) -> Optional[Dict[str, Any]]:
        """Парсит XML файл формы и извлекает структуру."""
        try:
            # Регистрируем namespace для корректного парсинга
            ET.register_namespace('v8', 'http://v8.1c.ru/8.1/data/core')
            ET.register_namespace('lf', 'http://v8.1c.ru/8.2/managed-application/logform')
            ET.register_namespace('app', 'http://v8.1c.ru/8.2/managed-application/core')
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Ищем элемент Form
            form_elem = root.find('.//{http://v8.1c.ru/8.3/MDClasses}Form')
            if form_elem is None:
                self.log("warning", f"Не найден элемент Form в файле: {xml_path.name}")
                return None
            
            # Извлекаем основные свойства формы
            form_data = {
                "name": "",
                "synonym": "",
                "comment": "",
                "form_type": "",
                "elements": [],
                "attributes": []
            }
            
            # Ищем свойства формы
            properties = form_elem.find('.//{http://v8.1c.ru/8.3/MDClasses}Properties')
            if properties is not None:
                # Имя формы
                name_elem = properties.find('.//{http://v8.1c.ru/8.3/MDClasses}Name')
                if name_elem is not None:
                    form_data["name"] = name_elem.text or ""
                
                # Синоним
                synonym_elem = properties.find('.//{http://v8.1c.ru/8.3/MDClasses}Synonym')
                if synonym_elem is not None:
                    content_elem = synonym_elem.find('.//{http://v8.1c.ru/8.1/data/core}content')
                    if content_elem is not None:
                        form_data["synonym"] = content_elem.text or ""
                
                # Комментарий
                comment_elem = properties.find('.//{http://v8.1c.ru/8.3/MDClasses}Comment')
                if comment_elem is not None:
                    form_data["comment"] = comment_elem.text or ""
                
                # Тип формы
                form_type_elem = properties.find('.//{http://v8.1c.ru/8.3/MDClasses}FormType')
                if form_type_elem is not None:
                    form_data["form_type"] = form_type_elem.text or ""
            
            # Ищем элементы формы (упрощенный парсинг)
            self._parse_form_elements(form_elem, form_data)
            
            return form_data
            
        except ET.ParseError as e:
            self.log("error", f"Ошибка парсинга XML в файле {xml_path.name}: {e}")
            return None
        except Exception as e:
            self.log("error", f"Неожиданная ошибка при обработке {xml_path.name}: {e}")
            return None

    def _parse_form_elements(self, form_elem, form_data: Dict[str, Any]):
        """Парсит элементы формы (упрощенная версия)."""
        try:
            # Ищем элементы формы
            elements = form_elem.findall('.//{http://v8.1c.ru/8.2/managed-application/logform}Form')
            for elem in elements:
                elem_data = {
                    "type": "FormElement",
                    "name": elem.get("name", ""),
                    "id": elem.get("id", "")
                }
                form_data["elements"].append(elem_data)
            
            # Ищем атрибуты формы
            attributes = form_elem.findall('.//{http://v8.1c.ru/8.2/managed-application/logform}Attribute')
            for attr in attributes:
                attr_data = {
                    "type": "Attribute",
                    "name": attr.get("name", ""),
                    "id": attr.get("id", "")
                }
                form_data["attributes"].append(attr_data)
                
        except Exception as e:
            self.log("warning", f"Ошибка при парсинге элементов формы: {e}")

    def generate_form_contract(self, form_data: Dict[str, Any], form_name: str) -> Dict[str, Any]:
        """Генерирует контракт формы."""
        contract = {
            "metadata_type": "Form",
            "name": form_data.get("name", form_name),
            "synonym": form_data.get("synonym", ""),
            "comment": form_data.get("comment", ""),
            "form_type": form_data.get("form_type", ""),
            "structure": {
                "elements_count": len(form_data.get("elements", [])),
                "attributes_count": len(form_data.get("attributes", [])),
                "elements": form_data.get("elements", []),
                "attributes": form_data.get("attributes", [])
            },
            "generated_at": str(Path().cwd()),
            "source": "XML Form Description"
        }
        
        return contract

    def process_form_file(self, xml_path: Path) -> bool:
        """Обрабатывает один файл формы."""
        try:
            # Парсим XML
            form_data = self.parse_form_xml(xml_path)
            if not form_data:
                return False
            
            # Генерируем контракт
            form_name = xml_path.stem
            contract = self.generate_form_contract(form_data, form_name)
            
            # Сохраняем контракт
            output_file = self.output_dir / f"{form_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(contract, f, ensure_ascii=False, indent=2)
            
            self.log("success", f"Создан контракт: {form_name}")
            return True
            
        except Exception as e:
            self.log("error", f"Ошибка при обработке {xml_path.name}: {e}")
            return False

    def generate(self) -> bool:
        """Основной метод генерации контрактов форм."""
        print("🔄 Генерация контрактов форм...")
        
        # Очищаем папку
        self.clean_output_directory()
        
        # Ищем файлы форм
        form_files = self.find_form_files()
        if not form_files:
            self.log("warning", "Файлы форм не найдены")
            self.print_logs()
            return False
        
        # Обрабатываем каждый файл
        success_count = 0
        for xml_path in form_files:
            if self.process_form_file(xml_path):
                success_count += 1
        
        # Выводим результаты
        self.log("summary", f"Обработано файлов: {len(form_files)}, успешно: {success_count}")
        self.print_logs()
        
        return success_count > 0 