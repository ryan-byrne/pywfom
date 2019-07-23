
/*

This code is meant to test the signal chain of the WFOM system's LEDs

Signal -> Arduino -> LED Controller -> LED -> Spectrometer

*/

#define greenLed   8
#define redLed     10
#define blueLed    7
#define limeLed    12

int leds[] = {greenLed, redLed, blueLed, limeLed};

void setup() {
  Serial.begin(9600);
  for (int i; i < sizeof(leds); i++){
    pinMode(leds[i], OUTPUT);
  }
}

void loop() {
  if (Serial.available() > 0) {
    char incomingByte;
    // Read new Byte
    incomingByte = Serial.read();

    // If byte is empty, ignore
    if (!incomingByte){
      return;
    }

    // Recieving a new command, clear all LEDs
    //clear();

    // Interpret Byte
    switch (incomingByte) {
      case 'L':
        digitalWrite(limeLed, HIGH);
        break;
      case 'l':
        digitalWrite(limeLed, LOW);
        break;
      case 'B':
        digitalWrite(blueLed, HIGH);
        break;
      case 'b':
        digitalWrite(blueLed, LOW);
        break;
      case 'R':
        digitalWrite(redLed, HIGH);
        break;
      case 'r':
        digitalWrite(redLed, LOW);
        break;
      case 'G':
        digitalWrite(greenLed, HIGH);
        break;
      case 'g':
        digitalWrite(greenLed, LOW);
        break;
    }
  }
}
