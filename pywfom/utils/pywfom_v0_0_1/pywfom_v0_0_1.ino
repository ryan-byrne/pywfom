int incomingByte;
int trigPin;
int ledPins[] = {};
int currentLed = 0;
int stimPins[] = {};
String msg;
bool strobing = false;

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
    // Deciphering message from serial port
    switch (msg.substring(0,1)) {
      case "l":
        updateLedPins(msg);
        break;
      case "T":
        toggleLed(msg);
        break;
      case "s":
        updateStimPins(msg);
        break;
      case "f":
        updateStimFunction(msg);
        break;
      case "t":
        updateTrigger(msg);
        break;
      case "S":
        // Toggle Strobing
        strobing != strobing;
        break;
      case "C":
        clearSettings();
        break;
    }
  }

  if ((digitalRead(trigPin)) && (strobing)){
    strobe();
  }

}

void strobe(){

  if (i > (sizeof(ledPins) / sizeof(ledPins[0]))){
    currentLed = 0;
  }

  digitalWrite(currentLed, HIGH);
  currentLed++;
  
}

void clearSettings(){
  incomingByte;
  trigPin;
  ledPins[] = {};
  stimPins[] = {};
  String msg;
  currentLed = 0;
  strobing = false;
}

void updateLedPins(String msg){

}

void updateStimPins(String msg){

}

void updateStimFunction(String msg){

}

void updateTrigger(String msg){

}
