#include <Arduino.h>

char response[10] = "<pywfom0.0.1>";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(response);
  delay(100);
}
