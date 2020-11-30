int incomingByte;
int trig;
int ledPins[] = {};
int stimPins[] = {};
String msg;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
}

void loop() {
  if (Serial.available() > 0){
    // Recieving new message over the Serial Port
    // Creating blank message
    String msg = "";
    while (Serial.available() > 0){
      // Reading the first byte of the message into a char
      int c = Serial.read();
      // Ignoring chars that are not numbers or letters, adding to message
      if (c<48){
        continue;
      }
      else{
        msg += char(c);
      }
      delay(1);
    }
  }

}
