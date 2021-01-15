import os
from setuptools import setup, find_packages

with open(os.path.join(os.getcwd(), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "pywfom",
    version = "0.0.1",
    author = "Ryan Byrne",
    author_email = "ryanbyrne142@gmail.com",
    keywords = "wide field optical mapping",
    url = "https://github.com/ryan-byrne/pyfom",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "pyserial",
        "numpy",
        "Pillow",
        "tqdm",
        "pyfiglet"
    ],
    entry_points={
        'console_scripts':[
            'wfom = pywfom:main',
            'wfom-archive = pywfom:archive',
            'wfom-viewer = pywfom:view',
            'wfom-quickstart = pywfom:quickstart'
        ] },
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>3.5',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta"
    ],
    project_urls={
        "Bug Reports":"https://github.com/ryan-byrne/pywfom/issues",
        "Hillman Lab":"https://hillmanlab.zuckermaninstitute.columbia.edu/"
    },
)
