from setuptools import setup, find_packages

setup(
    name="snapped-it",
    version="1.0.0",
    description="Cross-platform floating screen capture toolbar",
    author="Md Zarif Azfar",
    packages=find_packages(),
    py_modules=["main"],
    install_requires=[
        "PySide6>=6.5.0",
        "mss>=9.0.0",
        "pynput>=1.7.6",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "snapped-it=main:main",
        ],
    },
)
