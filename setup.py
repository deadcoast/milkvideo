#!/usr/bin/env python3
"""
Setup script for VideoMilker.
"""

from setuptools import find_packages
from setuptools import setup


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


setup(
    name="videomilker",
    version="1.0.0",
    author="VideoMilker Team",
    author_email="team@videomilker.com",
    description="An intuitive, tree-structured CLI interface for yt-dlp with visual feedback",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/videomilker/videomilker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Archiving",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Environment :: Console",
        "Framework :: Click",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "vmx=videomilker.main:main",
            "videomilker=videomilker.main:main",
            "vm=videomilker.main:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
