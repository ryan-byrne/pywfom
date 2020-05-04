import os
from setuptools import setup, find_packages

with open(os.path.join(os.getcwd(), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "openwfom",
    version = "0.0.1b15",
    author = "Ryan Byrne",
    author_email = "ryanbyrne142@gmail.com",
    keywords = "wide field optical mapping",
    url = "https://github.com/ryan-byrne/openwfom",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "pywinauto",
        "path",
        "pyfiglet",
        "pyserial",
        "psutil",
        "pyfiglet",
        "colorama",
        "termcolor"
    ],
    scripts=['bin/wfom-test','bin/wfom-run'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>3.5,!=3.7.6',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta"
    ],
    project_urls={
        "Bug Reports":"https://github.com/ryan-byrne/wfom/issues",
        "Hillman Lab":"https://hillmanlab.zuckermaninstitute.columbia.edu/"
    },
)
