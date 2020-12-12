int incomingByte;
int trigPin;
int ledPins[10];
int numLeds = 0;
int currentLed = 0;
int stimPins[10];
String msg;
boolean strobing = false;

void setup() {
  Serial.begin(115200);
  pinMode(10, OUTPUT);
  while (!Serial) {
    ;
  }
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
      delay(1);
    }
    // Deciphering message from serial port
    switch (msg.charAt(0)) {
      case 'p':
        updateLedPins(msg);
        break;
      case 'T':
        toggleLed(msg);
        break;
      case 's':
        updateStimPins(msg);
        break;
      case 'f':
        updateStimFunction(msg);
        break;
      case 't':
        updateTrigger(msg);
        break;
      case 'S':
        // Toggle Strobing
        strobing = !strobing;
        Serial.println(strobing);
        break;
      case 'C':
        clearSettings();
        break;
      case 'c':
        clearLeds();
        break;
    }
  }
  
  if (digitalRead(trigPin) && strobing){
    strobe();
  }
}

void strobe(){
  
  digitalWrite(ledPins[currentLed], LOW);
  currentLed++;

  if (currentLed > numLeds){
    currentLed = 0;
  }

  digitalWrite(ledPins[currentLed], HIGH);
  
}

void clearSettings(){
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
  digitalWrite(10, HIGH);
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

void toggleLed(String msg){
  clearLeds();
  int pin = msg.substring(1).toInt();
  digitalWrite(pin, HIGH);
}
