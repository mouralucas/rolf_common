from setuptools import setup, find_packages

VERSION = '0.0.10'
DESCRIPTION = 'Common package for all Rolf microservices'
LONG_DESCRIPTION = 'This package contains all base classes for database managers, sql models, services and pydantic schemas'

setup(
    name="rolf_common",
    author="Lucas Moura",
    version=VERSION,
    DESCRIPTION=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(include=['rolf_common', 'rolf_common.*']),
    install_requires=[
    ],
)
