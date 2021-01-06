int incomingByte;
int trigPin = 2;
int ledPins[4] = {7,8,10,12};
int numLeds = 4;
int currentLed = 0;
int stimPins[10];
String msg;
boolean strobing = false;
String ledNames[4] = {
  "blue",
  "green",
  "red",
  "orange"
};

void setup() {
  // ******
  pinMode(trigPin, INPUT);
  for (int i=0; i<4; i++){
    pinMode(ledPins[i], OUTPUT);
  }
  // ******
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  pinMode(10, OUTPUT);
  pinMode(2, INPUT);
}

void loop() {
  if (Serial.available() > 0){
    // Recieving new message over the Serial Port
    // Creating blank message
    String msg;
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
      delay(10);
    }
    // Deciphering message from serial port
    switch (msg.charAt(0)) {
      case 'p':
        updateLedPins(msg);
        break;
      case 'T':
        toggleLed(msg);
        break;
      case 'm':
        updateStimPins(msg);
        break;
      case 'f':
        updateStimFunction(msg);
        break;
      case 't':
        updateTrigger(msg);
        break;
      case 'S':
        // Turn on Strobing
        strobing = true;
        break;
      case 's':
        // Turn off Strobing
        strobing = false;
        break;
      case 'C':
        clearAllSettings();
        break;
      case 'c':
        clearLeds();
        break;
    }
  }
  Serial.flush();
  if (strobing){
    while(digitalRead(trigPin)){}
    nextLed();
    while(!digitalRead(trigPin)){}
  }

}

void nextLed(){
  digitalWrite(ledPins[currentLed], LOW);
  currentLed++;

  if (currentLed > numLeds-1){
    currentLed = 0;
  }
  digitalWrite(ledPins[currentLed], HIGH);

}

void clearAllSettings(){
  incomingByte;
  trigPin;
  int ledPins[] = {};
  int stimPins[] = {};
  String msg;
  currentLed = 0;
  numLeds = 0;
  strobing = false;
}

void clearLeds(){
  for (int i = 0; i < numLeds; i++){
    digitalWrite(ledPins[i], LOW);
  }
}

void updateLedPins(String msg){
  numLeds = 0;
  String pin = "";

  for (int i = 0; i < msg.length(); i++){
    if (msg[i]=='p'){
      if (pin == ""){
        continue;
      }
      else {
        ledPins[numLeds] = pin.toInt();
        pinMode(pin.toInt(), OUTPUT);
        numLeds++;
        pin = "";
      }
    }
    else {
      pin += msg[i];
    }
  }
}

void updateStimPins(String msg){

}

void updateStimFunction(String msg){

}

void updateTrigger(String msg){
  trigPin = msg.substring(1).toInt();
  pinMode(trigPin, INPUT);
}

void updateEncoders(String msg){
  // TODO Add encoders
}

void toggleLed(String msg){
  clearLeds();
  int pin = msg.substring(1).toInt();
  digitalWrite(pin, HIGH);
}
