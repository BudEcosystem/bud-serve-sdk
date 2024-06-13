import os
from typing import List, Set
from pathlib import Path
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)

def get_path(*filepath) -> str:
    return os.path.join(ROOT_DIR, *filepath)

def get_requirements() -> List[str]:
    """Get Python package dependencies from requirements.txt."""

    with open(get_path("requirements.txt")) as f:
        requirements = f.read().strip().split("\n")

    return requirements

setup(
    name='budserve',
    version='0.0.1',
    description='A python sdk for budserve inference engine',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BudEcosystem/bud-serve-sdk',
    packages=find_packages(include=['budserve', 'budserve.*']),
    install_requires=get_requirements(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache2 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
