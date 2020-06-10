# Python Module for the [OpenWFOM](https://hillmanlab.zuckermaninstitute.columbia.edu/content/optical-imaging-and-microscopy-development-and-dissemination) Imaging System

The ```openwfom``` Python Package and command line tool are ways to declare camera settings, test setup, and start an acquisition on an OpenWFOM imaging system.

## Getting Started

These instructions will help you get the necessary software installed.

***NOTE:*** Before following this installation guide, complete the hardware assembly instructions found on [This Wiki](https://github.com/ryan-byrne/wfom/wiki)

### Software Requirements

* [Python](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-python-from-the-command-line) - 3.5 and Up
* [Java Runtime](https://www.java.com/en/download/help/download_options.xml#windows) - 1.7 and Up
* [Andor SOLIS (4.30 and up)](http://my.andor.com/login.aspx) - Registration Required
* [Spinnaker SDK](https://www.flir.com/products/spinnaker-sdk/) - FLIR Webcam Drivers
* [Arduino IDE](https://www.arduino.cc/en/main/software) - Arduino Drivers



### Installation

#### Setting up the Virtual Environment

Firstly, ***```openwfom``` must be run within a virtual machine to avoid compability issues***. For more information on virtual machines, particularly Python's built-in '''venv''' follow [this link](https://docs.python.org/3/library/venv.html).

To start a new virtual machine, open a command prompt, navigate to where you would like to create the new directory, and enter:

``` cmd
python -m venv wfom
```

I have named my virtual environment ```wfom```, but it can be any name you choose. Next, activate the virtual environment by entering:

``` cmd
\wfom\Scripts\activate
```

Your virtual environment's name will appear to the left of your current directory as shown below:

```
(wfom) C:\Users\ryanb>
```

All Python scripts will now be run within our new virtual environment ```wfom```

#### Installing the ```openwfom``` Python Package with PIP

Make sure you have [PIP](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line) installed on your machine. Enter:

``` cmd
pip install openwfom
```

The ```openwfom``` Python Package is now installed in your Python ```site-packages```. ```wfom-test``` and ```wfom-run``` have also been added to your PATH to be used as **command line tools**. More on that later. 

### Test the Installation

We will now test to see if ```openwfom``` and it's required files were installed correctly. Start by opening a new instance of CMD and type:

``` cmd
wfom-test -v -y
```

The test script will run, automatically bypassing any errors it recieves, and print each message recieved to the command prompt. It will also generate a log file, whose path will be printed at the end of the script at:

```
/path/to/site-packages/openwfom/resources/logs
```

**Note:** *If any errors occur, post a screenshot of the command line and the output of ```pip freeze``` to this repository's [Issues Page](https://github.com/ryan-byrne/openwfom/issues).*

## Usage

This section provides information on how to use the ```openwfom``` package, as well as the command line arguments that were installed to the path.

### (Option 1) Using the Python Package

Using the ```openwfom``` Python Package simply requires importing it's ```wfom``` module. ```wfom```'s functions can now be used in your custom script.

``` python
from openwfom import wfom

wfom.run()
```

#### Available Classes

The OpenWFOM package is comprised of three classes: **Andor, Arduino, and Webcam**, which can be imported on their own.

For example, if I simply wanted to import the Arduino class from ```wfom``` I would write:

``` python
from openwfom import wfom

# Initiate the Arduino Class
a = wfom.Arduino("COM4")
# Call the strobe function to open the Strobe GUI
a.strobe()
```

### (Option 2) Running from the Command Line

During the ```pip``` installation of our ```openwfom``` package, there were two executable scripts that were installed to our PATH: ```wfom-test``` and ```wfom-run```. To run either, simply enter them into CMD.

```
wfom-test
```

or

```
wfom-run
```
#### Command Line Arguments

To run the **command line script** with more (or less) funtionality, optional command line arguments were built in:

* ```-q``` or ```--quiet``` runs the script in "Quiet Mode", without command line prints
*  ```-v``` or ```--verbose``` runs the script in "Verbose Mode", which prints each message on a successive line, and exports the log to a file.
*  ```-y``` or ```--auto_yes``` automatically continues whenever an error occurs

**Note:** *"Quiet" and "Verbose" modes cannot be run concurrently.*

For example, the following command would run an acquisition without command line prints, and automatically continue whenever an error occurs:

```
wfom-run -q -y
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ryan-byrne/wfom/tags).

## Authors

* **Ryan Byrne** - *Initial work* - [ryan-byrne](https://github.com/ryan-byrne)

See also the list of [contributors](https://github.com/ryan-byrne/wfom/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Beth Hillman and the rest of the LFOI Team
