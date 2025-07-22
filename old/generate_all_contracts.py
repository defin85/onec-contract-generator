"""
Мастер-скрипт для генерации всех контрактов метаданных конфигурации 1С.

Назначение:
Этот скрипт запускает генерацию контрактов метаданных и форм с возможностью
выборочного запуска отдельных компонентов.

Использование:
python generate_all_contracts.py --report-path "conf_reports/FullReport.txt" --conf-dir "conf_files"

Опции:
--skip-metadata    - Пропустить генерацию контрактов метаданных
--skip-forms       - Пропустить генерацию контрактов форм
--output-dir       - Базовая директория для сохранения контрактов
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

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

def run_command(cmd, description):
    """Запускает команду и выводит результат."""
    print(f"\n{'='*60}")
    print(f"Запуск: {description}")
    print(f"Команда: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.stdout:
            print("Вывод:")
            print(result.stdout)
        
        if result.stderr:
            print("Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} завершено успешно")
            return True
        else:
            print(f"❌ {description} завершено с ошибкой (код: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске {description}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Генерация всех контрактов метаданных конфигурации 1С",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--report-path", 
        required=True,
        help="Путь к текстовому файлу отчета по конфигурации"
    )
    
    parser.add_argument(
        "--conf-dir", 
        required=True,
        help="Путь к директории с файлами конфигурации (conf_files)"
    )
    
    parser.add_argument(
        "--output-dir", 
        default="metadata_contracts",
        help="Базовая директория для сохранения контрактов (по умолчанию: metadata_contracts)"
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
    
    args = parser.parse_args()
    
    # Проверяем существование файлов
    if not os.path.exists(args.report_path):
        print(f"❌ Файл отчета не найден: {args.report_path}")
        return 1
    
    if not os.path.exists(args.conf_dir):
        print(f"❌ Директория конфигурации не найдена: {args.conf_dir}")
        return 1
    
    print("🚀 Запуск генерации контрактов метаданных 1С")
    print(f"📄 Отчет: {args.report_path}")
    print(f"📁 Конфигурация: {args.conf_dir}")
    print(f"📂 Выходная директория: {args.output_dir}")
    
    success_count = 0
    total_count = 0
    
    # 1. Генерация контрактов метаданных
    if not args.skip_metadata:
        total_count += 1
        cmd = [
            sys.executable, "generate_contracts.py",
            args.report_path,
            "--output-dir", args.output_dir
        ]
        
        if run_command(cmd, "Генерация контрактов метаданных"):
            success_count += 1
    else:
        print("\n⏭️  Пропущена генерация контрактов метаданных")
    
    # 2. Генерация контрактов форм
    if not args.skip_forms:
        total_count += 1
        forms_output_dir = os.path.join(args.output_dir, "Формы")
        
        cmd = [
            sys.executable, "form_contracts_generator.py",
            "--conf-dir", args.conf_dir,
            "--output-dir", forms_output_dir
        ]
        
        if run_command(cmd, "Генерация контрактов форм"):
            success_count += 1
    else:
        print("\n⏭️  Пропущена генерация контрактов форм")
    
    # Итоговый отчет
    print(f"\n{'='*60}")
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*60}")
    print(f"✅ Успешно выполнено: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 Все операции выполнены успешно!")
        print(f"📂 Контракты сохранены в: {args.output_dir}")
        return 0
    else:
        print("⚠️  Некоторые операции завершились с ошибками")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 