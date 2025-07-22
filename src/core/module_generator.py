"""
Генератор контрактов модулей 1С.

Назначение:
Генерирует JSON-контракты для модулей объектов из XML-файлов.
"""

import os
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any

class ModuleGenerator:
    """Генератор контрактов модулей."""
    
    def __init__(self, conf_dir: str, output_dir: str):
        self.conf_dir = Path(conf_dir)
        self.output_dir = Path(output_dir)
        
    def clean_output_directory(self):
        """Очищает целевую папку от старых файлов контрактов модулей."""
        if self.output_dir.exists():
            print(f"  🧹 Очищаю целевую папку: {self.output_dir}")
            try:
                # Удаляем все файлы .json в папке
                for json_file in self.output_dir.glob("*.json"):
                    json_file.unlink()
                    print(f"    Удален: {json_file.name}")
                
                # Удаляем все подпапки (если есть)
                for subdir in self.output_dir.iterdir():
                    if subdir.is_dir():
                        shutil.rmtree(subdir)
                        print(f"    Удалена папка: {subdir.name}")
                
                print(f"  ✅ Целевая папка очищена успешно")
            except Exception as e:
                print(f"  ❌ Ошибка при очистке папки {self.output_dir}: {e}")
        else:
            print(f"  📁 Целевая папка не существует, будет создана: {self.output_dir}")
    
    def find_object_files(self) -> List[Path]:
        """Находит все XML файлы объектов в конфигурации."""
        object_files = []
        
        # Ищем файлы в папках объектов
        object_dirs = ['Catalogs', 'Documents', 'Reports', 'DataProcessors', 'ExternalDataProcessors']
        
        for obj_dir in object_dirs:
            obj_path = self.conf_dir / obj_dir
            if obj_path.exists():
                for xml_file in obj_path.rglob("*.xml"):
                    # Исключаем файлы форм
                    if not xml_file.name.startswith("Form"):
                        object_files.append(xml_file)
        
        return object_files
    
    def parse_object_xml(self, xml_path: Path) -> Dict[str, Any]:
        """Парсит XML файл объекта и извлекает информацию о модулях."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Определяем пространства имен
            namespaces = {
                'mdclass': 'http://v8.1c.ru/8.3/MDClasses',
                'core': 'http://v8.1c.ru/8.1/data/core'
            }
            
            object_data = {
                "name": xml_path.stem,
                "type": "Неопределено",
                "attributes": [],
                "tabular_sections": [],
                "forms": [],
                "modules": []
            }
            
            # Определяем тип объекта по пути
            path_parts = xml_path.parts
            for i, part in enumerate(path_parts):
                if part in ['Catalogs', 'Documents', 'Reports', 'DataProcessors', 'ExternalDataProcessors']:
                    object_data["type"] = part
                    break
            
            # Ищем реквизиты
            for attr in root.findall('.//mdclass:Attribute', namespaces):
                name_elem = attr.find('.//mdclass:Name', namespaces)
                type_elem = attr.find('.//core:Type', namespaces)
                
                if name_elem is not None:
                    attr_name = name_elem.text
                    attr_type = type_elem.text if type_elem is not None else "Неопределено"
                    
                    object_data["attributes"].append({
                        "name": attr_name,
                        "type": attr_type
                    })
            
            # Ищем табличные части
            for tab_section in root.findall('.//mdclass:TabularSection', namespaces):
                name_elem = tab_section.find('.//mdclass:Name', namespaces)
                
                if name_elem is not None:
                    section_name = name_elem.text
                    section_data = {
                        "name": section_name,
                        "columns": []
                    }
                    
                    # Ищем колонки табличной части
                    for col in tab_section.findall('.//mdclass:Attribute', namespaces):
                        col_name_elem = col.find('.//mdclass:Name', namespaces)
                        col_type_elem = col.find('.//core:Type', namespaces)
                        
                        if col_name_elem is not None:
                            col_name = col_name_elem.text
                            col_type = col_type_elem.text if col_type_elem is not None else "Неопределено"
                            
                            section_data["columns"].append({
                                "name": col_name,
                                "type": col_type
                            })
                    
                    object_data["tabular_sections"].append(section_data)
            
            # Ищем формы
            for form in root.findall('.//mdclass:Form', namespaces):
                name_elem = form.find('.//mdclass:Name', namespaces)
                
                if name_elem is not None:
                    form_name = name_elem.text
                    object_data["forms"].append(form_name)
            
            # Определяем модули (по умолчанию для каждого объекта)
            default_modules = [
                "ObjectModule",
                "ManagerModule", 
                "FormModule"
            ]
            
            object_data["modules"] = default_modules
            
            return object_data
            
        except Exception as e:
            print(f"  ❌ Ошибка при парсинге объекта {xml_path}: {e}")
            return {
                "name": xml_path.stem,
                "type": "Ошибка парсинга",
                "attributes": [],
                "tabular_sections": [],
                "forms": [],
                "modules": []
            }
    
    def generate_module_contract(self, xml_path: Path) -> Optional[Dict[str, Any]]:
        """Генерирует контракт модуля для одного объекта."""
        try:
            print(f"  📋 Обрабатываю объект: {xml_path.name}")
            
            # Парсим XML объекта
            object_data = self.parse_object_xml(xml_path)
            
            # Создаем контракт модуля
            contract = {
                "object_name": object_data["name"],
                "object_type": object_data["type"],
                "path": str(xml_path),
                "attributes": object_data["attributes"],
                "tabular_sections": object_data["tabular_sections"],
                "forms": object_data["forms"],
                "modules": object_data["modules"],
                "description": f"Контракт модуля для объекта {object_data['name']} типа {object_data['type']}"
            }
            
            return contract
            
        except Exception as e:
            print(f"  ❌ Ошибка при генерации контракта модуля для {xml_path}: {e}")
            return None
    
    def save_module_contract(self, contract: Dict[str, Any], xml_path: Path):
        """Сохраняет контракт модуля в JSON файл."""
        try:
            # Создаем имя файла контракта
            object_name = contract["object_name"]
            object_type = contract["object_type"]
            
            # Заменяем точки на подчеркивания для имени файла
            safe_name = object_name.replace('.', '_')
            safe_type = object_type.replace('.', '_')
            
            contract_filename = f"{safe_name}_{safe_type}_ModuleContract.json"
            contract_path = self.output_dir / contract_filename
            
            # Сохраняем контракт
            with open(contract_path, 'w', encoding='utf-8') as f:
                json.dump(contract, f, ensure_ascii=False, indent=4)
            
            print(f"  💾 Сохранен контракт: {contract_filename}")
            
        except Exception as e:
            print(f"  ❌ Ошибка при сохранении контракта модуля для {xml_path}: {e}")
    
    def generate(self) -> bool:
        """Генерирует контракты модулей."""
        try:
            print(f"  📁 Конфигурация: {self.conf_dir}")
            print(f"  📂 Выходная директория: {self.output_dir}")
            
            # Очищаем целевую папку
            self.clean_output_directory()
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Находим все файлы объектов
            object_files = self.find_object_files()
            print(f"  🔍 Найдено файлов объектов: {len(object_files)}")
            
            if not object_files:
                print("  ⚠️  Файлы объектов не найдены")
                return True
            
            # Обрабатываем каждый объект
            success_count = 0
            for xml_path in object_files:
                contract = self.generate_module_contract(xml_path)
                if contract:
                    self.save_module_contract(contract, xml_path)
                    success_count += 1
            
            print(f"\n  ✅ Обработано объектов: {success_count}/{len(object_files)}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации модулей: {e}")
            return False 