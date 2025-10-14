"""
Setup script for Snake of Despair.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="snake-of-despair",
    version="1.0.0",
    author="Kaulan Serzhanuly, Danila Kharitonenkov",
    author_email="kaulan.serzhanuly@sjsu.edu, danila.kharitonenkov@sjsu.edu",
    description="A horror twist on the classic Snake game with adaptive fear injection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/snake-of-despair",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Arcade",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "snake-of-despair=snake_of_despair.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "snake_of_despair": [
            "assets/audio/*",
            "assets/images/*", 
            "assets/video/*",
        ],
    },
    keywords="game, snake, horror, pygame, accessibility, python",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/snake-of-despair/issues",
        "Source": "https://github.com/yourusername/snake-of-despair",
        "Documentation": "https://github.com/yourusername/snake-of-despair#readme",
    },
)
