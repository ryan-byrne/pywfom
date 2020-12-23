.. _arduino:

Arduino Setup
=============

Running ``PyWFOM`` requires first setting up an
`Arduino Microcontroller <https://arduino.cc/>`_
to be used with the system.

Installing the Arduino IDE & Drivers
------------------------------------

`Download the IDE for your Operating System <https://www.arduino.cc/en/software/>`_
and follow the instructions on your screen.

Any required USB Drivers will be installed alongside the IDE.

Deploying to the Arduino
------------------------

1. Attach the Arduino you wish to use with your ``PyWFOM`` system to your machine via USB.

  * **NOTE:** `Arduino MEGA <https://store.arduino.cc/usa/mega-2560-r3/>`_ is suggested

2. Download the `pywfomArduino.ino <https://raw.githubusercontent.com/ryan-byrne/pywfom/master/files/pywfomArduino/pywfomArduino.ino>`_ file.

3. Start the **Arduino IDE**, and open the downloaded ``pywfomArduino.ino`` file

4. Verify the correct device and port are selected

.. figure:: correctport.png
  :align: center
  :width: 500

  These can be changed from the `Tools` Menu

5. Deploy the code to the Arduino

.. figure:: deploy.png
  :align: center
  :width: 500

  Wait until the code successfully deploys

6. ``PyWFOM`` is now able to send settings to your **Arduino**
