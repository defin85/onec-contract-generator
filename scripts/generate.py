#!/usr/bin/env python3
"""
Главный скрипт для генерации контрактов метаданных 1С.

Использование:
python scripts/generate.py                    # Интерактивный режим
python scripts/generate.py --help            # Справка
python scripts/generate.py --auto --conf-dir conf_files --report-path conf_reports/FullReport.txt
"""

import os
import sys
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.launcher import main

if __name__ == "__main__":
    main() 