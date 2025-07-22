"""
1C Contract Generator - Система генерации контрактов метаданных 1С

Основной пакет для генерации контрактов метаданных, форм и модулей 1С.
"""

__version__ = "2.0.0"
__author__ = "1C Contract Generator Team"
__description__ = "Система генерации контрактов метаданных 1С"

from .core.launcher import ContractGeneratorLauncher
from .core.metadata_generator import MetadataGenerator
from .core.form_generator import FormGenerator
from .core.module_generator import ModuleGenerator

__all__ = [
    'ContractGeneratorLauncher',
    'MetadataGenerator', 
    'FormGenerator',
    'ModuleGenerator'
] 