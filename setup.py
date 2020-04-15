import os
from setuptools import setup

with open(os.path.join(os.getcwd(), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "wfom",
    version = "0.0.1",
    author = "Ryan Byrne",
    author_email = "ryanbyrne142@gmail.com",
    keywords = "wide field optical mapping",
    url = "http://packages.python.org/wfom",
    py_modules=["wfom"],
    long_description=long_description,
    python_requires='>=3.5',
    project_urls={
        "Bug Reports":"https://github.com/ryan-byrne/wfom/issues",
        "Say Thanks":"https://saythanks.io/to/ryanbyrne142%40yahoo.com",
        "Hillman Lab":"http://orion.bme.columbia.edu/~hillman/"
    },
)
