#include <Arduino.h>
#include "PyWFOM.h"

PyWFOM wfom;

/*

Incoming Commands

First Letter:

  f = Return firmware version <f>

  t = Set Trigger Pin <t14>
  l = Set LEDs Pins<l6,12,15,>
  d = Set DAQ Pins<d5,7,>

  s = Set Stim Pins<s4,5,>

*/

void setup(){ wfom.Init(); }

void loop(){ wfom.Run(); }
