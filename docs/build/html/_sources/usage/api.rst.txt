.. _api:

API Documentation
=================

Camera Interface
----------------

.. code-block:: python

    from pywfom.imaging import Camera

    cam = Camera('webcam', 0) # Create webcam camera interface

    cam.set(height=550, width=450, framerate=15.0) # Establish settings

    print(cam.read()) # Print current frame

    cam.close() # Close camera

.. automodule:: pywfom.imaging
  :members:

Arduino Interface
-----------------

.. code-block:: python

    from pywfom.control import Arduino, list_ports

    ports = list_ports() # Gather a list of available COM ports

    port, name = ports[0] # Select the first port

    ard = Arduino(port=port) # Connect to Arduino at specified port

    ard.toggle_led(5) # Turn on LED at pin 5

.. automodule:: pywfom.control
  :members:

Available GUI's
---------------

.. automodule:: pywfom.viewing
  :members:
