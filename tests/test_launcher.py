"""
Тесты для главного запускатора.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Добавляем путь к src в PYTHONPATH
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.launcher import ContractGeneratorLauncher

class TestContractGeneratorLauncher:
    """Тесты для главного запускатора."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.launcher = ContractGeneratorLauncher()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Очистка после каждого теста."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Тест инициализации запускатора."""
        assert self.launcher.conf_dir is None
        assert self.launcher.report_path is None
        assert self.launcher.output_dir == "metadata_contracts"
        assert self.launcher.skip_metadata is False
        assert self.launcher.skip_forms is False
        assert self.launcher.skip_modules is False
    
    def test_print_banner(self, capsys):
        """Тест вывода баннера."""
        self.launcher.print_banner()
        captured = capsys.readouterr()
        assert "ГЕНЕРАТОР КОНТРАКТОВ 1С" in captured.out
    
    def test_command_line_mode(self):
        """Тест командного режима."""
        # Создаем временные файлы
        conf_dir = Path(self.temp_dir) / "conf_files"
        conf_dir.mkdir()
        
        report_file = Path(self.temp_dir) / "report.txt"
        report_file.write_text("test report")
        
        # Создаем mock args
        class MockArgs:
            conf_dir = str(conf_dir)
            report_path = str(report_file)
            output_dir = "test_output"
            skip_metadata = False
            skip_forms = True
            skip_modules = True
        
        self.launcher.command_line_mode(MockArgs())
        
        assert self.launcher.conf_dir == str(conf_dir)
        assert self.launcher.report_path == str(report_file)
        assert self.launcher.output_dir == "test_output"
        assert self.launcher.skip_metadata is False
        assert self.launcher.skip_forms is True
        assert self.launcher.skip_modules is True 