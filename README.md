# Wide Field Optical Mapping (WFOM)

This project is meant to create a streamlined interface to interact with Wide Field Optical Mapping (WFOM) Imaging Systems. 

## Getting Started

These instructions will help you get the necessary software installed onto your PC.

### Computer Requirements

```
Windows (8, 8.1, 10)
4GB RAM
2.68 GHZ Quad Core
850 MB/s continuous write Hard Drive
```

### Hardware Requirements

For a comprehensive list of hardware requirements, as well as how to assemble them, visit [This Wiki](https://link.to.wiki)

### Software Requirements

* [Python](https://www.python.org/downloads/) - 3.7 and Up
* [Java Runtime](https://java.com/en/download/) - 1.8 and Up
* [Andor SOLIS (4.30 and up)](http://www.andor.com/downloads) - Registration Required
* [Git](https://git-scm.com/download/win) - Latest Version

### Installation

Open up a Command Prompt and navigate to your machine's root directory by typing the following command:

```
cd /
```

Clone into the Git repository to download the required files.

```
git clone https://github.com/ryan-byrne/wfom.git
```

Navigate into the wfom directory, then run the setup.py script to install the neccessary Python packages.

```
cd wfom
python setup.py install
```

## Test the Installation

We will now test to see if the files were installed correctly.

```
python -m wfom --test
```

Once the diagnostic test is complete, any errors will be logged to a text file at:

```
resources/tests/TIMESTAMP_OF_TEST.txt
```

## Usage

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ryan-byrne/wfom/tags). 

## Authors

* **Ryan Byrne** - *Initial work* - [ryan-byrne](https://github.com/ryan-byrne)

See also the list of [contributors](https://github.com/ryan-byrne/wfom/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
