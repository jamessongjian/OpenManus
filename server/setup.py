from setuptools import setup, find_packages

setup(
    name="openmanus-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "websockets",
        "pydantic",
    ],
) 