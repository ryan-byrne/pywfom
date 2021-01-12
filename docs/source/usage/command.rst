.. _command:

Command Line Tools
==================

The simplest way to configure, acquire, and view runs is with one of :py:mod:`pywfom`'s
available `Command Line Tools`_.

=============== =================================================================
Command         Description
=============== =================================================================
wfom            Creates a :ref:`System Interface` and opens the :ref:`Main Frame`
--------------- -----------------------------------------------------------------
wfom-viewer     View :ref:`Acquisition Files` in the :ref:`Run Viewer`
--------------- -----------------------------------------------------------------
wfom-quickstart Quickly start an acquisition using the default settings
=============== =================================================================

wfom
----

Arguments
*********

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
  
