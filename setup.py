import os
from setuptools import setup


setup(
    name="sa-blueprint-sv",
    version="0.5.0",
    url="https://github.com/astutespruce/sa-blueprint-sv",
    license="MIT",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description="Custom reporting for South Atlantic Conservation Blueprint",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    # see Pipfile
    install_requires=[],
)
