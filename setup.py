#!/usr/bin/env python3
"""
Setup script для OneC Contract Generator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="onec-contract-generator",  # Изменено на более уникальное имя
    version="2.0.0",
    author="Your Name",  # Замените на ваше имя
    author_email="your.email@example.com",  # Замените на ваш email
    description="Система генерации контрактов метаданных 1С",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/1c-contract-generator",  # Замените на ваш репозиторий
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Основные зависимости (пока пустые, так как используем только стандартную библиотеку)
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "onec-contract-generate=core.launcher:main",
            "onec-contract-analyze=scripts.analyze:main",
            "onec-contract-test=scripts.test:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="1c, enterprise, metadata, contracts, generation, analysis",
    project_urls={
        "Bug Reports": "https://github.com/your-username/1c-contract-generator/issues",
        "Source": "https://github.com/your-username/1c-contract-generator",
        "Documentation": "https://github.com/your-username/1c-contract-generator#readme",
    },
) 