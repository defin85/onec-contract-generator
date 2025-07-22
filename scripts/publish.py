#!/usr/bin/env python3
"""
Скрипт для публикации OneC Contract Generator на PyPI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Выполняет команду и выводит результат."""
    print(f"🔄 {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - УСПЕШНО")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - ОШИБКА")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    
    return True

def clean_build():
    """Очищает папки сборки."""
    print("🧹 Очистка папок сборки...")
    
    build_dirs = ["build", "dist", "*.egg-info"]
    for pattern in build_dirs:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Удалена папка: {path}")
            elif path.is_file():
                path.unlink()
                print(f"  Удален файл: {path}")

def check_prerequisites():
    """Проверяет необходимые инструменты."""
    print("🔍 Проверка необходимых инструментов...")
    
    tools = [
        ("python", "Python"),
        ("pip", "pip"),
        ("twine", "twine"),
        ("build", "build"),
    ]
    
    for tool, name in tools:
        result = subprocess.run(f"{tool} --version", shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"  ✅ {name}: найдено")
        else:
            print(f"  ❌ {name}: НЕ НАЙДЕНО")
            print(f"    Установите: pip install {tool}")
            return False
    
    return True

def build_package():
    """Собирает пакет."""
    return run_command(
        "python -m build",
        "Сборка пакета"
    )

def check_package():
    """Проверяет собранный пакет."""
    return run_command(
        "twine check dist/*",
        "Проверка пакета"
    )

def upload_to_testpypi():
    """Загружает пакет на TestPyPI."""
    print("🚀 Загрузка на TestPyPI...")
    print("  Для загрузки на TestPyPI используйте:")
    print("  twine upload --repository testpypi dist/*")
    print("  Или для продакшн PyPI:")
    print("  twine upload dist/*")
    
    choice = input("\nХотите загрузить на TestPyPI сейчас? (y/N): ").strip().lower()
    if choice == 'y':
        return run_command(
            "twine upload --repository testpypi dist/*",
            "Загрузка на TestPyPI"
        )
    else:
        print("📦 Пакет готов к загрузке в папке dist/")
        return True

def main():
    """Основная функция."""
    print("🚀 ПУБЛИКАЦИЯ ONEC CONTRACT GENERATOR")
    print("=" * 50)
    
    # Проверяем, что мы в корневой папке проекта
    if not Path("setup.py").exists():
        print("❌ Ошибка: запустите скрипт из корневой папки проекта")
        sys.exit(1)
    
    # Проверяем инструменты
    if not check_prerequisites():
        print("❌ Не все необходимые инструменты установлены")
        sys.exit(1)
    
    # Очищаем старые сборки
    clean_build()
    
    # Собираем пакет
    if not build_package():
        print("❌ Ошибка при сборке пакета")
        sys.exit(1)
    
    # Проверяем пакет
    if not check_package():
        print("❌ Ошибка при проверке пакета")
        sys.exit(1)
    
    # Загружаем на PyPI
    if not upload_to_testpypi():
        print("❌ Ошибка при загрузке пакета")
        sys.exit(1)
    
    print("\n🎉 ПУБЛИКАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("📦 Пакет готов к использованию")

if __name__ == "__main__":
    main() 