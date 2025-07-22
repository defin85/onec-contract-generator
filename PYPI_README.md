# OneC Contract Generator

[![PyPI version](https://badge.fury.io/py/onec-contract-generator.svg)](https://badge.fury.io/py/onec-contract-generator)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Autonomous system for generating structured JSON contracts from 1C:Enterprise configurations**

## 🚀 Quick Start

```bash
# Install
pip install onec-contract-generator

# Generate contracts
onec-contract-generate --auto \
  --conf-dir "path/to/conf_files" \
  --report-path "path/to/report.txt" \
  --output-dir "metadata_contracts"
```

## ✨ Features

- **📊 Metadata Contracts**: Generate JSON contracts for 1C metadata objects
- **🎨 Form Contracts**: Extract form structure and controls
- **📝 Module Contracts**: Analyze object modules (future feature)
- **🔍 Semantic Search Ready**: Optimized structure for search engines
- **⚡ Fast Processing**: Handles large configurations efficiently
- **🛠️ Interactive Mode**: Step-by-step wizard for easy setup

## 📦 Installation

```bash
pip install onec-contract-generator
```

## 🎯 Usage

### Command Line

```bash
# Interactive mode
onec-contract-generate

# Automated mode
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\conf_files" \
  --report-path "C:\YourProject\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "metadata_contracts"
```

### Python API

```python
from src.core.metadata_generator import MetadataGenerator
from src.core.form_generator import FormGenerator

# Generate metadata contracts
generator = MetadataGenerator("report.txt", "output_dir")
success = generator.generate()

# Generate form contracts
form_gen = FormGenerator("conf_dir", "output_dir")
success = form_gen.generate()
```

## 📁 Output Structure

```
metadata_contracts/
├── Справочник_Номенклатура.json
├── Документ_ПоступлениеТоваров.json
├── Отчет_ОборотноСальдоваяВедомость.json
├── Перечисление_СтатусыДокументов.json
└── ОбщийМодуль_РаботаСФайлами.json
```

## 🔧 Configuration

The generator supports various 1C object types:
- **Основные объекты**: Справочники, Документы, Отчеты, Обработки
- **Регистры**: РегистрыСведений, РегистрыНакопления, РегистрыБухгалтерии
- **Планы**: ПланыВидовХарактеристик, ПланыОбмена, ПланыСчетов
- **Общие объекты**: Перечисления, ОбщиеМодули, ОбщиеКартинки
- **Сервисы**: HTTPСервисы, WebСервисы, XDTOПакеты

## 📚 Documentation

- [📖 Full Documentation](https://github.com/onec-contract-generator/onec-contract-generator#readme)
- [🚀 Usage Guide](https://github.com/onec-contract-generator/onec-contract-generator/blob/main/docs/USAGE.md)
- [📋 Examples](https://github.com/onec-contract-generator/onec-contract-generator/blob/main/docs/EXAMPLES.md)
- [📝 Changelog](https://github.com/onec-contract-generator/onec-contract-generator/blob/main/CHANGELOG.md)

## 🧪 Testing

```bash
# Run tests
onec-contract-test

# Or with pytest
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/onec-contract-generator/onec-contract-generator/blob/main/LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/onec-contract-generator/onec-contract-generator/issues)
- **Documentation**: [Full Documentation](https://github.com/onec-contract-generator/onec-contract-generator#readme)
- **Email**: support@onec-contract-generator.dev

---

**Made with ❤️ for the 1C:Enterprise community** 