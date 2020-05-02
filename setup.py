import os
from setuptools import setup

with open(os.path.join(os.getcwd(), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "OpenWFOM",
    version = "0.0.1b2",
    author = "Ryan Byrne",
    author_email = "ryanbyrne142@gmail.com",
    keywords = "wide field optical mapping",
    url = "https://github.com/ryan-byrne/OpenWFOM",
    include_package_data=True,
    py_modules=["wfom"],
    install_requires=[
        "colorama>-0.4.3",
        "path>-13.0.0",
        "psutil>-5.7.0",
        "pyfiglet>-0.8.post1",
        "pyserial>-3.4",
        "pywinauto>-0.6.3",
        "termcolor>-1.1.0"
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.5,!=3.7.6',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta"
    ],
    project_urls={
        "Bug Reports":"https://github.com/ryan-byrne/wfom/issues",
        "Hillman Lab":"http://orion.bme.columbia.edu/~hillman/"
    },
)
