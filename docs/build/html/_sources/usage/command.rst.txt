.. _command:

Command Line Tools
==================

Possibly the easiest way to configure and run your pyWFOM package is from the
command line using pyWFOM's Built-In **Command Line Tools**.

Available Commands
------------------

=============== ============================================================
Command         Description
=============== ============================================================
wfom            Runs pyWFOM and opens the Main Viewing Interface
--------------- ------------------------------------------------------------
wfom-quickstart Starts an instance of pyWFOM using the default settings
--------------- ------------------------------------------------------------
wfom-configure  Opens the pyWFOM Configuration Window to change settings
=============== ============================================================

Arguments
---------

======== ============== =========================================================
Argument   Name         Description
======== ============== =========================================================
  **-v**  **--verbose**   Determines whether pyWFOM prints to the console
-------- -------------- ---------------------------------------------------------
  **-t**  **--test**      Runs pyWFOM in 'Test Mode'
-------- -------------- ---------------------------------------------------------
  **-c**  **--config**   Include a string for the location of a JSON Config File
-------- -------------- ---------------------------------------------------------
  **-s**  **--solis**     Runs pyWFOM in 'Solis Mode'
======== ============== =========================================================

.. code-block:: bash

  wfom -v -c path/to/config/myConfiguration.json

The command above opens a new instance of pyWFOM in 'verbose mode', and with
the configuration settings from the file found at `path/to/config/myConfiguration.json`
