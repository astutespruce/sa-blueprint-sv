import os
from setuptools import setup


description = "South Atlantic Blueprint Simple Viewer and Custom Reporting"

if os.path.exists("README.md"):
    long_description = open("README.md").read()
else:
    long_description = description

setup(
    name="South Atlantic Blueprint Simple Viewer",
    version="0.5.0",
    url="https://github.com/astutespruce/sa-blueprint-sv",
    license="MIT",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description=description,
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=[],
)
