.. _configuration:
.. _JSON: https://www.json.org/json-en.html
.. _numpy: https://numpy.org/
.. _npz: https://numpy.org/doc/stable/reference/generated/numpy.savez.html

Acquisition Files
=================

Raw Data is stored as a individual frames in a ``run`` directory. ``frame``
file are numpy_ array, and saved as an npz_ file with the following structure.

Structure
---------
::

  run12
  ├── config.json
  ├── frame0.npz
  │   ├── cam0
  |   |   └── array
  │   ├── cam0
  |   |   └── array
  │   └──arduino
  |       └── message
  ├── frame1.npz
  .
  .
  .
  └── frameN.npz

Numpy Frame
-----------

JSON Configuration File
=======================

:py:mod:`pywfom` uses a JSON_ file to store various metadata and settings.

========== ========================================= ============== ===============
Setting    Description                                    Type          Example
========== ========================================= ============== ===============
user        Name or ID of individual who                 string       "rjb2202"
            ran the acquisition.
---------- ----------------------------------------- -------------- ---------------
mouse       Name or ID of the mouse the acquisition     string         "cm100"
            was conducted on.
---------- ----------------------------------------- -------------- ---------------
directory   Location data will be saved to                string      "C:/data"
---------- ----------------------------------------- -------------- ---------------
runs        Number of runs for given acquisition        int               5
---------- ----------------------------------------- -------------- ---------------
run_length  Length of each acquisition (in seconds)     float           10.0
---------- ----------------------------------------- -------------- ---------------
cameras     List of camera settings                     list        See `Cameras`_
---------- ----------------------------------------- -------------- ---------------
arduino     Dictionary of arduino settings              dict        See `Arduino`_
========== ========================================= ============== ===============

**NOTE:** It is highly recommended you only alter the your
:ref:`JSON Configuration File` , **do not directly edit the file itself**.

Example JSON Configuration
--------------------------

.. code-block:: JSON

  {
    "user":"rjb2202",
    "mouse":"cm100",
    "directory":"C:/data",
    "runs": 5,
    "run_length": 2.0
    "arduino": {}
    "cameras": []
  }

Arduino
-------

.. code-block:: JSON

  {
    "arduino": {
      "port": "COM4",
      "data_acquisition":[
        {
          "name":"encoder",
          "pin":20
        }
      ],
      "strobing": {
        "leds":[
          {
            "name":"blue",
            "pin":7
          },
          {
            "name":"green",
            "pin":8
          }
        ],
        "trigger":2
      },
      "stim": [
        {
          "name":"default",
          "type":"2PinStepper",
          "pins":{
            "step":5,
            "dim":6
          },
          "pre_stim":4.0,
          "stim":7.0,
          "post_stim":8.0
        }
      ]
    }
  }

Cameras
-------

.. code-block:: JSON

  {
    "cameras": [{
      "device": "test",
      "index": 0,
      "name": "cam1",
      "height": 564,
      "width": 420,
      "offset_x": 524,
      "offset_y": 157,
      "binning": "1x1",
      "dtype": "uint16",
      "master": true,
      "framerate": 20.0
    }, {
      "device": "test",
      "index": 0,
      "name": "cam3",
      "height": 500,
      "width": 400,
      "offset_x": 1,
      "offset_y": 50,
      "binning": "1x1",
      "dtype": "uint16",
      "master": false,
      "framerate": 10.0
    }]
  }

Default Configuration
---------------------
