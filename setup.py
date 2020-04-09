import os
from setuptools import setup


setup(
    name="sa-reports",
    version="0.1.0",
    # packages=[],
    url="https://github.com/brendan-ward/sa-reports",
    license="MIT",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description="Custom reporting for South Atlantic Conservation Blueprint",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    # see Pipfile
    install_requires=[],
)
