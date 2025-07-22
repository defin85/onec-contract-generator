#!/usr/bin/env python3
"""
Скрипт для тестирования системы генерации контрактов.

Использование:
python scripts/test.py    # Запуск всех тестов
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Основная функция."""
    print("🧪 Тестирование системы генерации контрактов")
    print("=" * 50)
    
    # Проверяем наличие тестов
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        print("❌ Папка tests не найдена")
        return 1
    
    # Запускаем тесты
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", str(tests_dir), "-v"
        ], capture_output=True, text=True)
        
        if result.stdout:
            print("Вывод тестов:")
            print(result.stdout)
        
        if result.stderr:
            print("Ошибки тестов:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Все тесты прошли успешно")
            return 0
        else:
            print("❌ Некоторые тесты не прошли")
            return 1
            
    except FileNotFoundError:
        print("⚠️  pytest не установлен. Установите: pip install pytest")
        return 1
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 