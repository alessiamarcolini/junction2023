import os
from typing import List

from setuptools import find_packages, setup


def read_dependencies(file_name: str = "base.txt") -> List[str]:
    requirements_path = os.path.join("requirements", file_name)
    with open(requirements_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


setup(
    name="junction",
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=read_dependencies(),
    python_requires=">=3.10, <3.12",
    include_package_data=True,
)
