from setuptools import setup, find_packages

setup(
    name="rolf_common",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.1",
        "pydantic==2.5.3",
        "sqlalchemy[asyncio]==2.0.15"
    ],
)
