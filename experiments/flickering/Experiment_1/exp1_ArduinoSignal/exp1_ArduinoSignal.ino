
/*

This code is meant to test the signal chain of the WFOM system's LEDs

Signal -> Arduino -> LED Controller -> LED -> Spectrometer

*/

#define greenLed   8
#define redLed     12
#define blueLed    7
#define limeLed    10

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
      case 'B':
        digitalWrite(blueLed, HIGH);
        break;
      case 'R':
        digitalWrite(redLed, HIGH);
        break;
      case 'G':
        digitalWrite(greenLed, HIGH);
        break;
      case 'C':
        clear();
        break;
    }
  }
}

void clear(){
  for (int i; i < sizeof(leds); i++){
    digitalWrite(leds[i], LOW);
  }
}
