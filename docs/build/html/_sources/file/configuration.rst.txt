.. _configuration:

Acquisition Files
=================

JSON Configuration File
=======================

``pyWFOM`` uses a JSON file to store various metadata and settings.

========== ============================================== ========= ===============
Setting    Description                                      Type     Example
========== ============================================== ========= ===============
user        Name or ID of individual who                    string    "rjb2202"
            ran the acquisition.
---------- ---------------------------------------------- --------- ---------------
mouse       Name or ID of the mouse the acquisition was    string     "cm100"
            conducted on.
---------- ---------------------------------------------- --------- ---------------
directory   Location data will be saved to                  string    "C:/data"
---------- ---------------------------------------------- --------- ---------------
runs        Number of runs for given acquisition              int      5
---------- ---------------------------------------------- --------- ---------------
run_length     Length of each acquisition (in seconds)        float      10.0
========== ============================================== ========= ===============

The JSON file also contains the settings for each Camera and Arduino Object.

**NOTE:** *It is highly recommended you only alter the your JSON Configuration
file from the provided GUI's, not directly editing the file itself.*

Example
-------

.. code-block:: JSON

  {
    "user":"rjb2202",
    "mouse":"cm100",
    "directory":"C:/data",
    "runs": 5,
    "run_length": 2.0
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
    },
    "cameras": [
      {
        "device":"andor",
        "index":0,
        "master":true,
        "name":"zyla",
        "dtype":"uint16",
        "height":2000,
        "width":2000,
        "offset_x":1,
        "offset_y":1,
        "binning":"2x2",
        "framerate":10.0
      }
    ]
  }

Default Configuration
---------------------
