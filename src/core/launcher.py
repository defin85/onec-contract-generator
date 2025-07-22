#!/usr/bin/env python3
"""
Единый запускатор для генерации контрактов метаданных 1С.

Назначение:
Этот модуль предоставляет унифицированный интерфейс для генерации всех типов контрактов:
- Контракты метаданных объектов (справочники, документы и т.д.)
- Контракты форм
- Контракты модулей

Поддерживает два режима работы:
1. Интерактивный режим - пошаговый мастер с подсказками
2. Командный режим - запуск через аргументы командной строки
"""

import os
import sys
import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import shutil

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

class ContractGeneratorLauncher:
    """Единый запускатор для генерации всех типов контрактов."""
    
    def __init__(self):
        self.conf_dir = None
        self.report_path = None
        self.output_dir = "metadata_contracts"
        self.skip_metadata = False
        self.skip_forms = False
        self.skip_modules = False
        
    def print_banner(self):
        """Выводит баннер приложения."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    ГЕНЕРАТОР КОНТРАКТОВ 1С                   ║
║                                                              ║
║  🎯 Контракты метаданных объектов                           ║
║  📋 Контракты форм                                          ║
║  🔧 Контракты модулей                                       ║
║                                                              ║
║  Версия: 2.0 | Python 3.x                                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def interactive_mode(self):
        """Интерактивный режим с пошаговым мастером."""
        self.print_banner()
        print("🎯 Запуск в интерактивном режиме")
        print("=" * 60)
        
        # Шаг 1: Выбор директории конфигурации
        self.conf_dir = self._get_conf_directory()
        
        # Шаг 2: Выбор файла отчета
        self.report_path = self._get_report_file()
        
        # Шаг 3: Выбор выходной директории
        self.output_dir = self._get_output_directory()
        
        # Шаг 4: Выбор компонентов для генерации
        self._select_components()
        
        # Шаг 5: Подтверждение и запуск
        self._confirm_and_run()
    
    def _get_conf_directory(self) -> str:
        """Интерактивный выбор директории конфигурации."""
        print("\n📁 Шаг 1: Выбор директории конфигурации")
        print("-" * 40)
        
        # Ищем папки с файлами конфигурации 1С
        default_paths = ["conf_files", "src", "."]
        existing_paths = []
        
        for path in default_paths:
            if os.path.exists(path):
                # Проверяем, есть ли в папке файлы конфигурации 1С
                has_config_files = False
                try:
                    for root, dirs, files in os.walk(path):
                        # Ищем папки с объектами 1С
                        if any(folder in dirs for folder in ['Catalogs', 'Documents', 'Reports', 'DataProcessors']):
                            has_config_files = True
                            break
                        # Ищем XML файлы объектов
                        for file in files:
                            if file.endswith('.xml') and not file.startswith('Form'):
                                has_config_files = True
                                break
                        if has_config_files:
                            break
                except:
                    pass
                
                if has_config_files:
                    existing_paths.append(path)
                    print(f"  ✅ {path} (найдены файлы конфигурации)")
                else:
                    print(f"  ⚠️  {path} (файлы конфигурации не найдены)")
        
        if existing_paths:
            print(f"\nНайдены директории с файлами конфигурации:")
            for i, path in enumerate(existing_paths, 1):
                print(f"  {i}. {path}")
            
            while True:
                try:
                    choice = input(f"\nВыберите номер (1-{len(existing_paths)}) или введите путь: ").strip()
                    
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(existing_paths):
                            selected_path = existing_paths[idx]
                            print(f"✅ Выбрана директория: {selected_path}")
                            return selected_path
                        else:
                            print("❌ Неверный номер. Попробуйте снова.")
                    else:
                        # Пользователь ввел путь
                        if os.path.exists(choice):
                            # Проверяем, есть ли файлы конфигурации
                            has_config = False
                            try:
                                for root, dirs, files in os.walk(choice):
                                    if any(folder in dirs for folder in ['Catalogs', 'Documents', 'Reports', 'DataProcessors']):
                                        has_config = True
                                        break
                                    for file in files:
                                        if file.endswith('.xml') and not file.startswith('Form'):
                                            has_config = True
                                            break
                                    if has_config:
                                        break
                            except:
                                pass
                            
                            if has_config:
                                print(f"✅ Выбрана директория: {choice}")
                                return choice
                            else:
                                print(f"⚠️  В директории не найдены файлы конфигурации 1С: {choice}")
                                print("   Ожидаются папки: Catalogs, Documents, Reports, DataProcessors")
                                print("   Или XML файлы объектов (не форм)")
                        else:
                            print(f"❌ Директория не найдена: {choice}")
                            
                except KeyboardInterrupt:
                    print("\n\n❌ Операция отменена пользователем.")
                    sys.exit(0)
        else:
            # Не найдено папок с файлами конфигурации
            print("⚠️  Не найдено папок с файлами конфигурации 1С")
            print("   Ожидаются папки: Catalogs, Documents, Reports, DataProcessors")
            print("   Или XML файлы объектов (не форм)")
            
            while True:
                path = input("Введите путь к директории с файлами конфигурации 1С: ").strip()
                if os.path.exists(path):
                    # Проверяем, есть ли файлы конфигурации
                    has_config = False
                    try:
                        for root, dirs, files in os.walk(path):
                            if any(folder in dirs for folder in ['Catalogs', 'Documents', 'Reports', 'DataProcessors']):
                                has_config = True
                                break
                            for file in files:
                                if file.endswith('.xml') and not file.startswith('Form'):
                                    has_config = True
                                    break
                            if has_config:
                                break
                    except:
                        pass
                    
                    if has_config:
                        print(f"✅ Выбрана директория: {path}")
                        return path
                    else:
                        print(f"⚠️  В директории не найдены файлы конфигурации 1С: {path}")
                        print("   Ожидаются папки: Catalogs, Documents, Reports, DataProcessors")
                        print("   Или XML файлы объектов (не форм)")
                else:
                    print(f"❌ Директория не найдена: {path}")
    
    def _get_report_file(self) -> str:
        """Интерактивный выбор файла отчета."""
        print("\n📄 Шаг 2: Выбор файла отчета")
        print("-" * 40)
        
        # Ищем файлы отчетов в стандартных местах
        report_paths = []
        search_dirs = ["conf_reports", "conf_report", "reports", self.conf_dir, "."]
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for file in os.listdir(search_dir):
                    # Ищем файлы отчетов конфигурации 1С
                    if (file.endswith(('.txt', '.report')) and 
                        any(keyword in file.lower() for keyword in ['report', 'отчет', 'конфигурац', 'config'])):
                        full_path = os.path.join(search_dir, file)
                        report_paths.append(full_path)
        
        if report_paths:
            print("Найдены файлы отчетов конфигурации:")
            for i, path in enumerate(report_paths, 1):
                print(f"  {i}. {path}")
            
            while True:
                try:
                    choice = input(f"\nВыберите номер (1-{len(report_paths)}) или введите путь: ").strip()
                    
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(report_paths):
                            selected_path = report_paths[idx]
                            print(f"✅ Выбран файл: {selected_path}")
                            return selected_path
                        else:
                            print("❌ Неверный номер. Попробуйте снова.")
                    else:
                        # Пользователь ввел путь
                        if os.path.exists(choice):
                            # Проверяем, что это текстовый файл
                            if choice.endswith(('.txt', '.report')):
                                print(f"✅ Выбран файл: {choice}")
                                return choice
                            else:
                                print(f"⚠️  Файл должен быть текстовым (.txt или .report): {choice}")
                        else:
                            print(f"❌ Файл не найден: {choice}")
                            
                except KeyboardInterrupt:
                    print("\n\n❌ Операция отменена пользователем.")
                    sys.exit(0)
        else:
            # Не найдено файлов отчетов
            print("⚠️  Не найдено файлов отчетов конфигурации")
            print("   Ожидаются файлы с именами: *report*.txt, *отчет*.txt, *config*.txt")
            print("   Или файлы с расширением .report")
            
            while True:
                path = input("Введите путь к файлу отчета конфигурации: ").strip()
                if os.path.exists(path):
                    # Проверяем, что это текстовый файл
                    if path.endswith(('.txt', '.report')):
                        print(f"✅ Выбран файл: {path}")
                        return path
                    else:
                        print(f"⚠️  Файл должен быть текстовым (.txt или .report): {path}")
                else:
                    print(f"❌ Файл не найден: {path}")
    
    def _get_output_directory(self) -> str:
        """Интерактивный выбор выходной директории."""
        print("\n📂 Шаг 3: Выбор выходной директории")
        print("-" * 40)
        
        # Предлагаем варианты
        default_output = "metadata_contracts"
        current_dir = os.getcwd()
        
        print("Варианты размещения результатов:")
        print(f"  1. 📁 Локальная папка: {default_output}")
        print(f"  2. 📁 Текущая директория: {current_dir}")
        print(f"  3. 📁 Абсолютный путь (например: C:\\YourProject\\YourConfig\\metadata_contracts)")
        print(f"  4. 📁 Рядом с конфигурацией: {os.path.dirname(self.conf_dir)}\\metadata_contracts")
        
        while True:
            try:
                choice = input("\nВыберите вариант (1-4) или введите путь: ").strip()
                
                if choice == "1":
                    print(f"✅ Используется локальная папка: {default_output}")
                    return default_output
                elif choice == "2":
                    print(f"✅ Используется текущая директория: {current_dir}")
                    return current_dir
                elif choice == "3":
                    path = input("Введите абсолютный путь: ").strip()
                    if path:
                        # Создаем папку, если не существует
                        try:
                            os.makedirs(path, exist_ok=True)
                            print(f"✅ Создана/используется папка: {path}")
                            return path
                        except Exception as e:
                            print(f"❌ Ошибка создания папки: {e}")
                    else:
                        print("❌ Путь не может быть пустым.")
                elif choice == "4":
                    suggested_path = os.path.join(os.path.dirname(self.conf_dir), "metadata_contracts")
                    try:
                        os.makedirs(suggested_path, exist_ok=True)
                        print(f"✅ Создана/используется папка: {suggested_path}")
                        return suggested_path
                    except Exception as e:
                        print(f"❌ Ошибка создания папки: {e}")
                else:
                    # Пользователь ввел путь
                    if choice:
                        try:
                            os.makedirs(choice, exist_ok=True)
                            print(f"✅ Создана/используется папка: {choice}")
                            return choice
                        except Exception as e:
                            print(f"❌ Ошибка создания папки: {e}")
                    else:
                        print("❌ Путь не может быть пустым.")
                        
            except KeyboardInterrupt:
                print("\n\n❌ Операция отменена пользователем.")
                sys.exit(0)
    
    def _select_components(self):
        """Интерактивный выбор компонентов для генерации."""
        print("\n🔧 Шаг 4: Выбор компонентов для генерации")
        print("-" * 40)
        
        components = [
            ("Контракты метаданных объектов", "metadata"),
            ("Контракты форм", "forms"),
            ("Контракты модулей", "modules")
        ]
        
        print("Доступные компоненты:")
        for i, (name, key) in enumerate(components, 1):
            print(f"  {i}. {name}")
        
        print("\nВыберите компоненты для генерации:")
        print("  'all' - все компоненты")
        print("  '1,2,3' - конкретные компоненты")
        print("  '1 2' - конкретные компоненты через пробел")
        
        while True:
            try:
                choice = input("\nВаш выбор: ").strip().lower()
                
                if choice == 'all':
                    self.skip_metadata = False
                    self.skip_forms = False
                    self.skip_modules = False
                    print("✅ Выбраны все компоненты")
                    break
                else:
                    # Парсим выбор пользователя
                    selected = set()
                    for part in choice.replace(',', ' ').split():
                        if part.isdigit():
                            idx = int(part) - 1
                            if 0 <= idx < len(components):
                                selected.add(components[idx][1])
                    
                    if selected:
                        self.skip_metadata = "metadata" not in selected
                        self.skip_forms = "forms" not in selected
                        self.skip_modules = "modules" not in selected
                        
                        print("✅ Выбраны компоненты:")
                        if not self.skip_metadata:
                            print("  - Контракты метаданных объектов")
                        if not self.skip_forms:
                            print("  - Контракты форм")
                        if not self.skip_modules:
                            print("  - Контракты модулей")
                        break
                    else:
                        print("❌ Неверный выбор. Попробуйте снова.")
                        
            except KeyboardInterrupt:
                print("\n\n❌ Операция отменена пользователем.")
                sys.exit(0)
    
    def _confirm_and_run(self):
        """Подтверждение настроек и запуск генерации."""
        print("\n🎯 Шаг 5: Подтверждение настроек")
        print("-" * 40)
        
        print("Параметры генерации:")
        print(f"  📁 Конфигурация: {self.conf_dir}")
        print(f"  📄 Отчет: {self.report_path}")
        print(f"  📂 Выходная директория: {self.output_dir}")
        print(f"  🔧 Компоненты:")
        if not self.skip_metadata:
            print("    ✅ Контракты метаданных")
        if not self.skip_forms:
            print("    ✅ Контракты форм")
        if not self.skip_modules:
            print("    ✅ Контракты модулей")
        
        while True:
            try:
                choice = input("\nЗапустить генерацию? (y/n): ").strip().lower()
                
                if choice in ['y', 'yes', 'да', 'д']:
                    print("\n🚀 Запуск генерации...")
                    self.run_generation()
                    break
                elif choice in ['n', 'no', 'нет', 'н']:
                    print("❌ Генерация отменена.")
                    sys.exit(0)
                else:
                    print("❌ Пожалуйста, введите 'y' или 'n'.")
                    
            except KeyboardInterrupt:
                print("\n\n❌ Операция отменена пользователем.")
                sys.exit(0)
    
    def run_generation(self):
        """Запускает генерацию выбранных компонентов."""
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК ГЕНЕРАЦИИ КОНТРАКТОВ")
        print("=" * 60)
        
        success_count = 0
        total_count = 0
        
        # 1. Генерация контрактов метаданных
        if not self.skip_metadata:
            total_count += 1
            print(f"\n📊 Генерация контрактов метаданных...")
            if self._run_metadata_generation():
                success_count += 1
                print("✅ Контракты метаданных сгенерированы успешно")
            else:
                print("❌ Ошибка при генерации контрактов метаданных")
        
        # 2. Генерация контрактов форм
        if not self.skip_forms:
            total_count += 1
            print(f"\n📋 Генерация контрактов форм...")
            if self._run_forms_generation():
                success_count += 1
                print("✅ Контракты форм сгенерированы успешно")
            else:
                print("❌ Ошибка при генерации контрактов форм")
        
        # 3. Генерация контрактов модулей
        if not self.skip_modules:
            total_count += 1
            print(f"\n🔧 Генерация контрактов модулей...")
            if self._run_modules_generation():
                success_count += 1
                print("✅ Контракты модулей сгенерированы успешно")
            else:
                print("❌ Ошибка при генерации контрактов модулей")
        
        # Итоговый отчет
        print(f"\n{'='*60}")
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print(f"{'='*60}")
        print(f"✅ Успешно выполнено: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 Все операции выполнены успешно!")
            print(f"📂 Контракты сохранены в: {self.output_dir}")
        else:
            print("⚠️  Некоторые операции завершились с ошибками")
        
        print(f"\n📂 Результаты сохранены в: {os.path.abspath(self.output_dir)}")
    
    def _run_metadata_generation(self) -> bool:
        """Запускает генерацию контрактов метаданных."""
        try:
            # Здесь будет вызов нового генератора метаданных
            from .metadata_generator import MetadataGenerator
            
            generator = MetadataGenerator(self.report_path, self.output_dir)
            return generator.generate()
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def _run_forms_generation(self) -> bool:
        """Запускает генерацию контрактов форм."""
        try:
            # Здесь будет вызов нового генератора форм
            from .form_generator import FormGenerator
            
            forms_output_dir = os.path.join(self.output_dir, "Формы")
            generator = FormGenerator(self.conf_dir, forms_output_dir)
            return generator.generate()
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def _run_modules_generation(self) -> bool:
        """Запускает генерацию контрактов модулей."""
        try:
            # Здесь будет вызов нового генератора модулей
            from .module_generator import ModuleGenerator
            
            modules_output_dir = os.path.join(self.output_dir, "Модули")
            generator = ModuleGenerator(self.conf_dir, modules_output_dir)
            return generator.generate()
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def command_line_mode(self, args):
        """Командный режим работы."""
        self.conf_dir = args.conf_dir
        self.report_path = args.report_path
        self.output_dir = args.output_dir
        self.skip_metadata = args.skip_metadata
        self.skip_forms = args.skip_forms
        self.skip_modules = args.skip_modules
        
        print("🚀 Запуск в командном режиме")
        self.run_generation()

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Единый запускатор для генерации контрактов метаданных 1С",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Автоматический режим (без интерактивных вопросов)"
    )
    
    parser.add_argument(
        "--conf-dir",
        help="Директория с файлами конфигурации"
    )
    
    parser.add_argument(
        "--report-path",
        help="Путь к файлу отчета по конфигурации"
    )
    
    parser.add_argument(
        "--output-dir",
        default="metadata_contracts",
        help="Выходная директория для контрактов (по умолчанию: metadata_contracts)"
    )
    
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="Пропустить генерацию контрактов метаданных"
    )
    
    parser.add_argument(
        "--skip-forms",
        action="store_true",
        help="Пропустить генерацию контрактов форм"
    )
    
    parser.add_argument(
        "--skip-modules",
        action="store_true",
        help="Пропустить генерацию контрактов модулей"
    )
    
    args = parser.parse_args()
    
    launcher = ContractGeneratorLauncher()
    
    if args.auto:
        # Командный режим
        if not args.conf_dir or not args.report_path:
            print("❌ В автоматическом режиме обязательны параметры --conf-dir и --report-path")
            sys.exit(1)
        
        launcher.command_line_mode(args)
    else:
        # Интерактивный режим
        launcher.interactive_mode()

if __name__ == "__main__":
    main() 