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
    name="onec-contract-generator",
    version="2.2.0",
    author="1C Contract Generator Team",
    author_email="support@onec-contract-generator.dev",
    description="Autonomous system for generating structured JSON contracts from 1C:Enterprise configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onec-contract-generator/onec-contract-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",

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
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Используем только стандартную библиотеку Python
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
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
    keywords="1c, enterprise, metadata, contracts, generation, analysis, json, xml, documentation",
    project_urls={
        "Bug Reports": "https://github.com/onec-contract-generator/onec-contract-generator/issues",
        "Source": "https://github.com/onec-contract-generator/onec-contract-generator",
        "Documentation": "https://github.com/onec-contract-generator/onec-contract-generator#readme",
        "Changelog": "https://github.com/onec-contract-generator/onec-contract-generator/blob/main/CHANGELOG.md",
    },
) 