# Python Package for the [OpenWFOM](https://hillmanlab.zuckermaninstitute.columbia.edu/content/optical-imaging-and-microscopy-development-and-dissemination) Imaging System

The ```openwfom``` Python Package and command line tool are ways to declare camera settings, test setup, and start an acquisition on an OpenWFOM imaging system.

## Getting Started

These instructions will help you get the necessary software installed.

***NOTE:*** Before following this installation guide, complete the hardware assembly instructions found on [This Wiki](https://github.com/ryan-byrne/wfom/wiki)

### Software Requirements

* [Python](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-python-from-the-command-line) - 3.5 and Up
* [Andor SDK3](https://andor.oxinst.com/products/software-development-kit/) - Andor Camera Drivers
* [Spinnaker SDK](https://www.flir.com/products/spinnaker-sdk/) - FLIR Webcam Drivers
* [Arduino IDE](https://www.arduino.cc/en/main/software) - Arduino Drivers

### Installation

#### 1) Setting up the Virtual Environment

The ```openwfom``` Python Package **should be installed and run within a virtual machine** to avoid compability issues.

For more information on virtual machines, particularly Python's built-in **```venv```** follow [this link](https://docs.python.org/3/library/venv.html).

#### 2) Installing the ```openwfom``` Python Package with PIP

Make sure you have [PIP](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line) installed on your machine then enter:

``` posh
> pip install openwfom
```

The ```openwfom``` Python Package is now installed in your Python Virtual Machine's ```site-packages```.

## Usage

This section provides information on how to use the ```openwfom``` package.

### (Option 1) Using OpenWFOM in Python

Using the ```openwfom``` Package in Python simply requires importing one of ```openwfom```'s modules.
``` python
from openwfom.imaging import spinnaker
```
We can then create an object using ```spinnaker```'s ```Camera()``` class.
``` python
flir = spinnaker.Camera(0, "Flir1")
```
And print the current frame until ```CTRL+C``` is pressed.
```python
while True:
    try:
        print(flir.frame)
    except KeyboardInterrupt:
        break
flir.close()
```
For a full list of available modules and their corrresponding methods consult the [OpenWFOM Documentation]().

#### Available Classes

The OpenWFOM package contains  

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ryan-byrne/wfom/tags).

## Authors

* **Ryan Byrne** - *Initial work* - [ryan-byrne](https://github.com/ryan-byrne)

See also the list of [contributors](https://github.com/ryan-byrne/wfom/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

## Acknowledgments

* Beth Hillman and the rest of the LFOI Team
