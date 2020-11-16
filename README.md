# Python Package for the [OpenWFOM](https://hillmanlab.zuckermaninstitute.columbia.edu/content/optical-imaging-and-microscopy-development-and-dissemination) Imaging System

The ```pywfom``` Python Package and command line tool are ways to declare camera settings, test setup, and start an acquisition on an OpenWFOM imaging system.

## Compatible Cameras

* [Andor SDK3]() - Andor Cameras (Neo, Zyla)
* [Spinnaker SDK]() - FLIR Cameras (Blackfly, Blackfly S)
* [Other USB Webcams]() - Also compatible with most USB Webcams

## Usage

To install ```pywfom``` and test your installation run:

```bash
pip install pywfom; wfom --test
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ryan-byrne/wfom/tags).

## Authors

* **Ryan Byrne** - *Initial work* - [ryan-byrne](https://github.com/ryan-byrne)

See also the list of [contributors](https://github.com/ryan-byrne/wfom/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

## Acknowledgments

* Beth Hillman and the rest of the LFOI Team
