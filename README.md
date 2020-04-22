# OpenWFOM

This repository stores the required software for the OpenWFOM system.

## Getting Started

These instructions will help you get the necessary software installed.

***NOTE:*** Before following this installation guide, complete the hardware assembly instructions found on [This Wiki](https://github.com/ryan-byrne/wfom/wiki)

### Software Requirements

* [Python](https://www.python.org/downloads/) - 3.6 and Up
* [Java Runtime](https://java.com/en/download/) - 1.8 and Up
* [Andor SOLIS (4.30 and up)](http://www.andor.com/downloads) - Registration Required
* [PIP](https://pip.pypa.io/en/stable/installing/) Install Option 1
* [Git](https://git-scm.com/download/win) - Install Option 2

### Installation

#### (Option 1) As a Python Package

The easiest way to use ```wfom``` is by importing its Python package directly into an existing script.

It must be first installed alongside your existing Python Packages using ```pip``` from the command line.

Open a new instance of CMD, and enter:

```
pip install wfom
```

You can now import the module and run any of its functions, as the ```example.py``` script does below.

```
import wfom

wfom.test()
```

#### (Option 2) As a Command Line Script

Open up a Command Prompt and navigate to your machine's root directory by typing the following command:

```
cd /
```

Clone into the Git repository to download the required files.

```
git clone https://github.com/ryan-byrne/wfom.git
```

Once the download is completed, navigate into the ```/wfom``` directory, and run the ```setup.py``` script
to install the necessary Python packages.

```
cd wfom
python setup.py install
```

### Test the Installation

We will now test to see if the files were installed correctly. Start by opening a new instance of CMD.

#### (Option 1) Test Python Package

Start Python from the command line.

```
python
```

Import the package,

```
>>> import wfom
```

And run the test function:

```
>>> wfom.test()
```

#### (Option 2) Test Command Line Script

**NOTE** ***The command line script can only be run from the ```C:/wfom``` directory***

```
python wfom.py --test
```

Once the diagnostic test is complete, any errors will be logged to a text file at:

```
C:/wfom/resources/tests/TIMESTAMP_OF_TEST.txt
```

## Usage

This section provides information on how to run the ```wfom``` script, as well as the command line arguments at your disposal

### (Option 1) Running the Python Package

As previously stated, running the ```wfom``` Python Package simply requires importing it into an existing script.

```
import wfom

wfom.run()
```

#### Available Classes

The OpenWFOM package is comprised of three classes: *Andor, Arduino, and Webcam*, which can be imported on their own. 

For example, if I simply wanted to import the Arduino class from ```wfom``` I would write:

```
from wfom import Arduino

# Initiate the Arduino Class
a = Arduino("COM4")
# Call the strobe function to open the Strobe GUI
a.strobe()
```

### (Option 2) Running from the Command Line

To run the script from the command line, while inside the ```/wfom``` directory type:

```
python wfom.py
```

***NOTE:*** If you've navigated to a different directory in the command prompt, you must explicitly refer to the location of ```wfom.py``` i.e.:

```
python C:\wfom\wfom.py
```

#### Command Line Arguments

There are also optional command line arguments which can be used to alter the information fed back from the command prompt, which can help streamline bug testing. They are:

* ```-q``` or ```--quiet``` runs the script in "Quiet Mode", without command line prints
*  ```-t``` or ```--test``` runs the script in "Test Mode", which we should have already run during the installation
*  ```-y``` automatically continues whenever an error occurs

For example, the following command would run without command line prints, and automatically continue whenever an error occurs:

```
python wfom.py -q -y
```

#### Running from the Batch File

Alternatively, if you'd prefer to avoid using the command prompt altogether, you can run the ```wfom.py``` script by opening the ```OpenWFOM.bat``` batch file, found at:

```
C:\wfom\OpenWFOM.bat
```

***NOTE*** This file can be copy and pasted wherever you'd like for better accessibility.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ryan-byrne/wfom/tags).

## Authors

* **Ryan Byrne** - *Initial work* - [ryan-byrne](https://github.com/ryan-byrne)

See also the list of [contributors](https://github.com/ryan-byrne/wfom/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Beth Hillman and the rest of the LFOI Team
