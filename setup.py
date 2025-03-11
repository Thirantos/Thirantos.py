from setuptools import setup, find_packages

setup(
    name="Thirantos",
    version="2025.0.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "sqlalchemy"
    ],
)