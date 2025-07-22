"""
Модуль для генерации контрактов форм из конфигурации 1С.

Назначение:
Этот модуль анализирует XML-описания форм и BSL-модули для создания структурированных 
JSON-контрактов, описывающих архитектуру форм. Контракты включают информацию о 
реквизитах формы, элементах управления, командах и контексте выполнения.

Структура контракта формы:
{
  "owner": "Справочник.ДокументыПредприятия",
  "name": "ФормаЭлемента", 
  "context": ["НаКлиенте", "НаСервере"],
  "attributes": [
    { "name": "Объект", "type": "СправочникОбъект.ДокументыПредприятия" }
  ],
  "controls": [
    { "name": "Наименование", "type": "ПолеВвода" }
  ],
  "commands": [
    { "name": "МояКоманда", "action": "МояКомандаНаКлиенте" }
  ]
}

Использование:
python form_contracts_generator.py --conf-dir conf_files --output-dir metadata_contracts/Формы
"""

import os
import sys
import argparse
import json
import re
import xml.etree.ElementTree as ET
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

# Настройка кодировки для корректного отображения кириллицы в Windows
if sys.platform == "win32":
    import locale
    
    # Устанавливаем кодировку консоли
    os.system('chcp 65001 > nul')
    
    # Устанавливаем локаль для корректного отображения
    try:
        locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except:
            pass
    
    # Устанавливаем переменную окружения для принудительного использования UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class FormContractGenerator:
    """Генератор контрактов для форм 1С."""
    
    def __init__(self, conf_dir: str, output_dir: str, clean_output: bool = True):
        self.conf_dir = Path(conf_dir)
        self.output_dir = Path(output_dir)
        self.clean_output = clean_output
        
        # Очищаем целевую папку перед началом работы
        if self.clean_output:
            self.clean_output_directory()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_output_directory(self):
        """Очищает целевую папку от старых файлов контрактов форм."""
        if self.output_dir.exists():
            print(f"Очищаю целевую папку: {self.output_dir}")
            try:
                # Удаляем все файлы .json в папке
                for json_file in self.output_dir.glob("*.json"):
                    json_file.unlink()
                    print(f"  Удален: {json_file.name}")
                
                # Удаляем все подпапки (если есть)
                for subdir in self.output_dir.iterdir():
                    if subdir.is_dir():
                        shutil.rmtree(subdir)
                        print(f"  Удалена папка: {subdir.name}")
                
                print(f"Целевая папка очищена успешно")
            except Exception as e:
                print(f"Ошибка при очистке папки {self.output_dir}: {e}")
        else:
            print(f"Целевая папка не существует, будет создана: {self.output_dir}")
    
    def find_form_files(self) -> List[Path]:
        """Находит все файлы Form.xml в конфигурации."""
        form_files = []
        for form_file in self.conf_dir.rglob("Form.xml"):
            form_files.append(form_file)
        return form_files
    
    def parse_form_xml(self, form_path: Path) -> Dict[str, Any]:
        """Универсальный парсер формы 1С: рекурсивно ищет элементы управления, реквизиты и команды с глубоким анализом типов данных."""
        try:
            tree = ET.parse(form_path)
            root = tree.getroot()

            form_data = {
                "attributes": [],
                "controls": [],
                "commands": [],
                "object_type": "Неопределено",
                "tabular_sections": []
            }

            control_keywords = [
                'Button', 'Field', 'Table', 'Group', 'AutoCommandBar', 'Panel', 'Tab', 'Label', 'Input', 'ComboBox', 'CheckBox', 'RadioButton', 'Picture', 'Hyperlink', 'List', 'Tree', 'Grid', 'Calendar', 'Chart', 'Splitter', 'Page', 'CommandBar', 'TextBox', 'TextEdit', 'SpinEdit', 'DateEdit', 'TimeEdit', 'PasswordEdit', 'NumberEdit', 'DocumentEdit', 'OrganizationEdit', 'CounterpartyEdit', 'UserEdit', 'FileEdit', 'FolderEdit', 'ReferenceEdit', 'ValueEdit', 'FormItem'
            ]

            attributes_dict = {}
            tabular_sections_dict = {}

            def extract_type(element):
                # Пробуем разные варианты атрибута типа
                for key in ["Type", "Тип", "DataType", "datatype", "type"]:
                    t = element.get(key)
                    if t:
                        return t
                return "Неопределено"

            def extract_object_type(element):
                # Ищем тип основного объекта формы
                for key in ["Object", "Объект", "MainObject", "MainObjectType"]:
                    obj_type = element.get(key)
                    if obj_type:
                        return obj_type
                return "Неопределено"

            def extract_tabular_section_info(element):
                # Извлекаем информацию о табличных частях
                tab_info = {
                    "name": element.get('name') or element.get('Name'),
                    "type": extract_type(element),
                    "columns": []
                }
                
                # Ищем колонки табличной части
                for child in element:
                    if child.tag.endswith('Column') or child.tag.endswith('Колонка'):
                        col_name = child.get('name') or child.get('Name')
                        col_type = extract_type(child)
                        if col_name:
                            tab_info["columns"].append({
                                "name": col_name,
                                "type": col_type
                            })
                
                return tab_info

            def walk(element):
                tag = element.tag
                
                # Определяем тип основного объекта формы
                if form_data["object_type"] == "Неопределено":
                    obj_type = extract_object_type(element)
                    if obj_type != "Неопределено":
                        form_data["object_type"] = obj_type
                
                # Реквизиты
                if tag.endswith('Attribute'):
                    name = element.get('name') or element.get('Name')
                    if name:
                        attr_type = extract_type(element)
                        attributes_dict[name] = attr_type
                        form_data["attributes"].append({
                            "name": name,
                            "type": attr_type
                        })
                
                # Табличные части
                if tag.endswith('TabularSection') or tag.endswith('ТабличнаяЧасть'):
                    tab_info = extract_tabular_section_info(element)
                    if tab_info["name"]:
                        tabular_sections_dict[tab_info["name"]] = tab_info
                        form_data["tabular_sections"].append(tab_info)
                
                # Команды
                if tag.endswith('Command'):
                    name = element.get('name') or element.get('Name') or element.get('CommandName')
                    if name:
                        form_data["commands"].append({
                            "name": name,
                            "action": "Неопределено"
                        })
                
                # Элементы управления
                for kw in control_keywords:
                    if kw in tag:
                        name = element.get('name') or element.get('Name')
                        if name:
                            # Если есть команда внутри элемента управления
                            cmd_name = element.get('CommandName')
                            if cmd_name:
                                form_data["commands"].append({
                                    "name": cmd_name,
                                    "action": f"{cmd_name} (из элемента управления)"
                                })
                            
                            # Определяем тип элемента управления
                            ctrl_type = extract_type(element)
                            
                            # Дополнительный анализ типа для специфических элементов
                            if kw in ['Table', 'Tree', 'Grid']:
                                # Для таблиц и деревьев ищем связанную табличную часть
                                for tab_name, tab_info in tabular_sections_dict.items():
                                    if tab_name.lower() in name.lower() or name.lower() in tab_name.lower():
                                        ctrl_type = f"Таблица({tab_info['type']})"
                                        break
                            
                            elif kw in ['Field', 'Input', 'TextBox', 'TextEdit', 'NumberEdit', 'DateEdit']:
                                # Для полей ввода ищем связанный реквизит
                                if name in attributes_dict:
                                    ctrl_type = attributes_dict[name]
                                else:
                                    # Ищем по частичному совпадению
                                    for attr_name, attr_type in attributes_dict.items():
                                        if attr_name.lower() in name.lower() or name.lower() in attr_name.lower():
                                            ctrl_type = attr_type
                                            break
                            
                            form_data["controls"].append({
                                "name": name,
                                "type": ctrl_type if ctrl_type != "Неопределено" else kw
                            })
                        break
                
                # Рекурсивно обходим детей
                for child in element:
                    walk(child)

            walk(root)

            # После обхода: для controls, если type == kw (т.е. не найден явно), ищем по имени среди attributes
            for ctrl in form_data["controls"]:
                if ctrl["type"] in control_keywords or ctrl["type"] == "Неопределено":
                    attr_type = attributes_dict.get(ctrl["name"])
                    if attr_type:
                        ctrl["type"] = attr_type
                    else:
                        # Ищем по частичному совпадению
                        for attr_name, attr_type in attributes_dict.items():
                            if attr_name.lower() in ctrl["name"].lower() or ctrl["name"].lower() in attr_name.lower():
                                ctrl["type"] = attr_type
                                break

            if not form_data["attributes"] and not form_data["controls"] and not form_data["commands"]:
                print(f"Предупреждение: Не удалось извлечь данные из XML файла {form_path}")
                print(f"Доступные теги в корне: {[elem.tag for elem in root]}")

            return form_data

        except ET.ParseError as e:
            print(f"Ошибка парсинга XML файла {form_path}: {e}")
            return {"attributes": [], "controls": [], "commands": [], "object_type": "Неопределено", "tabular_sections": []}
    
    def parse_bsl_module(self, module_path: Path) -> Dict[str, Any]:
        """Парсит BSL-модуль формы для извлечения контекста и типов с глубоким анализом."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_data = {
                "context": [],
                "attribute_types": {},
                "command_actions": {},
                "variable_types": {},
                "form_attributes": {}
            }
            
            # Определяем контекст выполнения
            if "&НаКлиенте" in content:
                module_data["context"].append("НаКлиенте")
            if "&НаСервере" in content:
                module_data["context"].append("НаСервере")
            if "&НаКлиентеНаСервере" in content:
                module_data["context"].append("НаКлиентеНаСервере")
            
            # Извлекаем типы реквизитов формы (более точный подход)
            # Ищем объявления типа "Перем ИмяРеквизита;"
            var_pattern = r'Перем\s+(\w+);'
            variables = re.findall(var_pattern, content)
            
            # Ищем типы в комментариях или объявлениях
            # Формат: // ИмяРеквизита - ТипДанных
            type_pattern = r'//\s*(\w+)\s*-\s*([^\n\r]+)'
            type_matches = re.findall(type_pattern, content)
            
            for var_name, var_type in type_matches:
                # Очищаем тип от лишних символов
                var_type = var_type.strip().rstrip(';').rstrip(',')
                module_data["attribute_types"][var_name] = var_type
            
            # Ищем реквизиты формы (Форма.Реквизит)
            form_attr_pattern = r'Форма\.(\w+)\s*=\s*([^;\n]+)'
            form_attrs = re.findall(form_attr_pattern, content)
            
            for attr_name, attr_value in form_attrs:
                # Пытаемся определить тип по значению
                if 'Новый' in attr_value:
                    # Новый объект
                    new_pattern = r'Новый\s+(\w+)'
                    new_match = re.search(new_pattern, attr_value)
                    if new_match:
                        module_data["form_attributes"][attr_name] = new_match.group(1)
                elif 'Справочники.' in attr_value:
                    module_data["form_attributes"][attr_name] = "СправочникСсылка"
                elif 'Документы.' in attr_value:
                    module_data["form_attributes"][attr_name] = "ДокументСсылка"
                elif 'Перечисления.' in attr_value:
                    module_data["form_attributes"][attr_name] = "ПеречислениеСсылка"
                elif 'Пользователи.' in attr_value:
                    module_data["form_attributes"][attr_name] = "ПользовательСсылка"
                elif 'Сотрудники.' in attr_value:
                    module_data["form_attributes"][attr_name] = "СотрудникСсылка"
                elif 'ТаблицаЗначений' in attr_value:
                    module_data["form_attributes"][attr_name] = "ТаблицаЗначений"
                elif 'Массив' in attr_value:
                    module_data["form_attributes"][attr_name] = "Массив"
                elif 'Структура' in attr_value:
                    module_data["form_attributes"][attr_name] = "Структура"
                elif 'Соответствие' in attr_value:
                    module_data["form_attributes"][attr_name] = "Соответствие"
                elif 'СписокЗначений' in attr_value:
                    module_data["form_attributes"][attr_name] = "СписокЗначений"
                elif 'Запрос' in attr_value:
                    module_data["form_attributes"][attr_name] = "Запрос"
                elif 'РезультатЗапроса' in attr_value:
                    module_data["form_attributes"][attr_name] = "РезультатЗапроса"
                elif 'НаборЗаписей' in attr_value:
                    module_data["form_attributes"][attr_name] = "НаборЗаписей"
                elif 'РегистрНакопления' in attr_value:
                    module_data["form_attributes"][attr_name] = "РегистрНакопления"
                elif 'РегистрСведений' in attr_value:
                    module_data["form_attributes"][attr_name] = "РегистрСведений"
                elif 'РегистрБухгалтерии' in attr_value:
                    module_data["form_attributes"][attr_name] = "РегистрБухгалтерии"
                elif 'РегистрРасчета' in attr_value:
                    module_data["form_attributes"][attr_name] = "РегистрРасчета"
                elif 'ТекущаяДата' in attr_value or 'ТекущаяДатаСеанса' in attr_value:
                    module_data["form_attributes"][attr_name] = "Дата"
                elif 'Истина' in attr_value or 'Ложь' in attr_value:
                    module_data["form_attributes"][attr_name] = "Булево"
                elif attr_value.strip().isdigit():
                    module_data["form_attributes"][attr_name] = "Число"
                elif attr_value.strip().startswith('"') and attr_value.strip().endswith('"'):
                    module_data["form_attributes"][attr_name] = "Строка"
                else:
                    module_data["form_attributes"][attr_name] = "Неопределено"
            
            # Извлекаем действия команд (более точный подход)
            # Ищем процедуры и функции
            proc_pattern = r'Процедура\s+(\w+)\s*\([^)]*\)'
            func_pattern = r'Функция\s+(\w+)\s*\([^)]*\)'
            
            procedures = re.findall(proc_pattern, content)
            functions = re.findall(func_pattern, content)
            
            # Определяем контекст для каждой процедуры/функции
            lines = content.split('\n')
            current_proc = None
            
            for line in lines:
                line = line.strip()
                
                # Ищем начало процедуры/функции
                proc_match = re.search(r'Процедура\s+(\w+)', line)
                func_match = re.search(r'Функция\s+(\w+)', line)
                
                if proc_match:
                    current_proc = proc_match.group(1)
                    # Определяем контекст
                    if '&НаКлиенте' in line:
                        module_data["command_actions"][current_proc] = f"{current_proc}НаКлиенте"
                    elif '&НаСервере' in line:
                        module_data["command_actions"][current_proc] = f"{current_proc}НаСервере"
                    elif '&НаКлиентеНаСервере' in line:
                        module_data["command_actions"][current_proc] = f"{current_proc}НаКлиентеНаСервере"
                    else:
                        module_data["command_actions"][current_proc] = f"{current_proc} (контекст не определен)"
                
                elif func_match:
                    current_proc = func_match.group(1)
                    # Определяем контекст
                    if '&НаКлиенте' in line:
                        module_data["command_actions"][current_proc] = f"{current_proc}НаКлиенте"
                    elif '&НаСервере' in line:
                        module_data["command_actions"][current_proc] = f"{current_proc}НаСервере"
                    elif '&НаКлиентеНаСервере' in line:
                        module_data["command_actions"][current_proc] = f"{current_proc}НаКлиентеНаСервере"
                    else:
                        module_data["command_actions"][current_proc] = f"{current_proc} (контекст не определен)"
                
                elif line.startswith('КонецПроцедуры') or line.startswith('КонецФункции'):
                    current_proc = None
            
            return module_data
            
        except Exception as e:
            print(f"Ошибка парсинга BSL модуля {module_path}: {e}")
            return {"context": [], "attribute_types": {}, "command_actions": {}, "variable_types": {}, "form_attributes": {}}
    
    def determine_owner_type(self, form_path: Path) -> str:
        """Определяет тип владельца формы на основе пути."""
        parts = form_path.parts
        
        # Ищем тип объекта в пути
        for i, part in enumerate(parts):
            if part in ["Catalogs", "Documents", "Reports", "DataProcessors", "CommonForms"]:
                if i + 1 < len(parts):
                    owner_name = parts[i + 1]
                    if part == "Catalogs":
                        return f"Справочник.{owner_name}"
                    elif part == "Documents":
                        return f"Документ.{owner_name}"
                    elif part == "Reports":
                        return f"Отчет.{owner_name}"
                    elif part == "DataProcessors":
                        return f"Обработка.{owner_name}"
                    elif part == "CommonForms":
                        return f"ОбщаяФорма.{owner_name}"
        
        return "Неопределено"
    
    def generate_form_contract(self, form_path: Path) -> Optional[Dict[str, Any]]:
        """Генерирует контракт для одной формы с глубоким анализом типов."""
        print(f"Обрабатываю форму: {form_path}")
        
        # Определяем имя формы (берем имя папки Forms)
        form_name = form_path.parent.parent.name
        
        # Определяем владельца
        owner = self.determine_owner_type(form_path)
        
        # Парсим XML формы
        form_data = self.parse_form_xml(form_path)
        
        # Ищем и парсим BSL модуль
        module_path = form_path.parent / "Ext" / "Form" / "Module.bsl"
        module_data = {}
        if module_path.exists():
            module_data = self.parse_bsl_module(module_path)
        
        # Объединяем данные
        contract = {
            "owner": owner,
            "name": form_name,
            "context": module_data.get("context", []),
            "object_type": form_data.get("object_type", "Неопределено"),
            "attributes": form_data["attributes"],
            "controls": form_data["controls"],
            "commands": form_data["commands"],
            "tabular_sections": form_data.get("tabular_sections", [])
        }
        
        # Уточняем типы реквизитов из BSL
        for attr in contract["attributes"]:
            # Сначала проверяем типы из BSL-модуля
            if attr["name"] in module_data.get("attribute_types", {}):
                attr["type"] = module_data["attribute_types"][attr["name"]]
            elif attr["name"] in module_data.get("form_attributes", {}):
                attr["type"] = module_data["form_attributes"][attr["name"]]
        
        # Уточняем типы элементов управления
        for ctrl in contract["controls"]:
            # Если тип не определен или это ключевое слово, ищем в BSL
            if ctrl["type"] in ["Неопределено", "Field", "Input", "TextBox", "TextEdit", "NumberEdit", "DateEdit"]:
                # Ищем в form_attributes по имени
                if ctrl["name"] in module_data.get("form_attributes", {}):
                    ctrl["type"] = module_data["form_attributes"][ctrl["name"]]
                # Ищем в attribute_types по имени
                elif ctrl["name"] in module_data.get("attribute_types", {}):
                    ctrl["type"] = module_data["attribute_types"][ctrl["name"]]
        
        # Уточняем действия команд из BSL
        for cmd in contract["commands"]:
            if cmd["name"] in module_data.get("command_actions", {}):
                cmd["action"] = module_data["command_actions"][cmd["name"]]
        
        return contract
    
    def save_form_contract(self, contract: Dict[str, Any], form_path: Path):
        """Сохраняет контракт формы в JSON файл."""
        owner = contract["owner"]
        form_name = contract["name"]
        
        # Создаем имя файла контракта
        if owner != "Неопределено":
            contract_filename = f"{owner}.{form_name}.json"
        else:
            contract_filename = f"{form_name}.json"
        
        contract_path = self.output_dir / contract_filename
        
        print(f"Сохраняю контракт формы: {contract_path}")
        with open(contract_path, 'w', encoding='utf-8') as f:
            json.dump(contract, f, ensure_ascii=False, indent=2)
    
    def generate_all_form_contracts(self):
        """Генерирует контракты для всех найденных форм."""
        form_files = self.find_form_files()
        print(f"Найдено {len(form_files)} файлов форм")
        
        for form_path in form_files:
            contract = self.generate_form_contract(form_path)
            if contract:
                self.save_form_contract(contract, form_path)
        
        print(f"Генерация контрактов форм завершена. Файлы сохранены в: {self.output_dir}")

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Генерация контрактов форм из конфигурации 1С.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--conf-dir", default="conf_files", 
                       help="Директория с файлами конфигурации")
    parser.add_argument("--output-dir", default="metadata_contracts/Формы", 
                       help="Директория для сохранения контрактов форм")
    parser.add_argument("--test-form", 
                       help="Тестирование на конкретной форме (например, ДокументыПредприятия.ФормаЭлемента)")
    parser.add_argument("--no-clean", action="store_true",
                       help="Не очищать целевую папку перед началом работы")
    
    args = parser.parse_args()
    
    generator = FormContractGenerator(args.conf_dir, args.output_dir, clean_output=not args.no_clean)
    
    if args.test_form:
        # Тестирование на конкретной форме
        print(f"Тестирование на форме: {args.test_form}")
        # Здесь можно добавить логику для тестирования конкретной формы
        form_files = generator.find_form_files()
        for form_path in form_files:
            if args.test_form in str(form_path):
                contract = generator.generate_form_contract(form_path)
                if contract:
                    print("Сгенерированный контракт:")
                    print(json.dumps(contract, ensure_ascii=False, indent=2))
                    generator.save_form_contract(contract, form_path)
                break
    else:
        # Генерация для всех форм
        generator.generate_all_form_contracts()

if __name__ == "__main__":
    main() 