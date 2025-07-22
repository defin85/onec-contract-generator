"""
Парсеры для различных форматов файлов 1С.

Содержит парсеры для XML файлов, BSL модулей и текстовых отчетов.
"""

from .xml_parser import XMLParser
from .bsl_parser import BSLParser
from .report_parser import ReportParser

__all__ = [
    'XMLParser',
    'BSLParser',
    'ReportParser'
] 