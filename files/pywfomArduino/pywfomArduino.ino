#include <Stepper.h>

// Serial message variables
char incomingChar;
char receivedChars[32];
boolean msgComplete = false;
boolean receivingMsg = false;
char msg[32];
char c;
char pin[2];
char val[4];

// LED Settings
int currentLed = 0;
int numLeds = 0;
int trigPin;
int ledPins[10];
boolean strobing = false;

// DAQ Settings
int numDaq = 0;
int daqPins[10];

// Stepper Settings
int stimPins[4];
int stepsPerRevolution;
int numStim = 0;
int stepperPos = 0;
Stepper stim(stepsPerRevolution, stimPins[0], stimPins[1]);

// Index Settings
int idx = 0;
int midx = 0;
int pidx = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
}

void loop() {
  
  readMsg(); // Check Serial message
  parseMsg(); // Interpret message

  if (strobing){
    nextLed();
  }
  
  returnData();
}

void readMsg(){
  
  static int idx = 0;
  
  while (Serial.available() > 0){

    incomingChar = Serial.read();
    if ( receivingMsg == true ) {
      if ( incomingChar == '>' ) {
        receivingMsg = false;
        msgComplete = true;
        receivedChars[idx] = '\0';
        idx = 0;
      }
      else {
        receivedChars[idx] = incomingChar;
        idx++;
      }
    }
    else if ( incomingChar == '<' ) {
      receivingMsg = true;
    }
    delay(10);
  }
}

void parseMsg(){
  
  if ( msgComplete == true ) {
    switch ( receivedChars[0] ) {
      case 'l':
        updateLedPins();
        break;
      case 'S':
        strobing = true;
        break;
      case 's':
        strobing = false;
        break;
      case 'd':
        updateDaqPins();
        break;
      case 'm':
        updateStim();
        break;
      case 'c':
        clearLeds();
        break;
      case 't':
        trigPin = int(receivedChars[1]);
        break;
      case 'T':
        toggleLed();
        break;
      case 'p':
        setStep();
        break;
    }
    
    msgComplete = false;
  }
}

void returnData(){
   
  midx = 0;

  if ( strobing ) {
    msg[midx++] = 'S';
    itoa( currentLed, pin , 10 );
    for ( int j=0; j<2; j++ ) {
      if (!pin[j]) { continue; }
      else { msg[midx++] = pin[j]; }
    }
  }
  else {
    msg[midx++] = 's';
  }
  msg[midx++] = '_';
  msg[midx++] = 'd';
  
  for ( int i=0; i<numDaq; i++ ) {
    itoa( digitalRead(daqPins[i]), val , 10 );
    for ( int j=0; j<2; j++ ) {
      if (!val[j]) { continue; }
      else { msg[midx++] = val[j]; }
    }
    msg[midx++] = ',';
  }

  msg[midx++] = 'm';
  itoa( stepperPos, val, 10 );
  for ( int i=0; i<sizeof(val); i++ ) {
    msg[midx++] = val[i];
  }
  msg[midx++] = '\0';
  Serial.println(msg);
}

void nextLed(){
  
  while(digitalRead(trigPin)){};
  digitalWrite(ledPins[currentLed], LOW);
  currentLed++;
  if (currentLed > numLeds-1){currentLed = 0;}  
  digitalWrite(ledPins[currentLed], HIGH);
  while(!digitalRead(trigPin)){}
  
}

void updateStim() {
  // 
  // <m15,16,17,18,.200>
  pidx = 0;
  idx = 0;
  boolean recordPins = false;
  
  for ( int i=1; i<sizeof(receivedChars); i++ ) {
    
    c = receivedChars[i];
    if ( !c ) { continue; }
    else if ( c == ',' ) {
      pinMode( atoi(pin), OUTPUT);
      stimPins[idx++] = atoi(pin);
      pidx = 0;
    }
    else if ( c == '.' ) { recordPins = true; }
    else if ( !recordPins ) { val[pidx++] = c; }
    else { pin[pidx++] = c; }
    
  }

  stepsPerRevolution = atoi( val );

  if ( numStim == 4 ) { Stepper stim( stepsPerRevolution, stimPins[0], stimPins[1], stimPins[2], stimPins[3] ); }
  else { Stepper stim( stepsPerRevolution, stimPins[0], stimPins[1]); }
  
}

void setStep() {
  idx = 0;
  for ( int i=1; i<sizeof(receivedChars); i++ ) {
    c = receivedChars[i];
    if ( !c ) { continue; }
    else if ( c == ',' ) {
      val[idx] = '\0'; 
      stim.setSpeed(atoi(val));
      idx = 0;
    }
    else { val[idx++] = c; } 
  }
  val[idx] = '\0';
  stim.step(atoi(val));
  stepperPos += atoi(val);
}

void updateLedPins(){

  idx = 0;
  numLeds = 0;
  
  for ( int i=1; i<sizeof(receivedChars); i++ ) {
    
    c = receivedChars[i];
    
    if (int(c) == 0){ continue; }
    else if ( c == ',' ){
      pin[idx] = '\0';
      ledPins[numLeds] = atoi(pin);
      numLeds++;
      pinMode( atoi(pin), OUTPUT );
      idx = 0;
    }
    else {
      pin[idx] = c;
      idx++;
    }
  }
}

void updateDaqPins(){

  idx = 0;
  numDaq = 0;
  
  for ( int i=1; i<sizeof(receivedChars); i++ ) {
    
    c = receivedChars[i];
    
    if (int(c) == 0){
      continue;
    }
    else if ( c == ',' ){
      pin[idx] = '\0';
      daqPins[numDaq] = atoi(pin);
      numDaq++;
      pinMode( atoi(pin), OUTPUT );
      idx = 0;
    }
    else {
      pin[idx] = c;
      idx++;
    }
  }
}

void clearAllSettings(){
  strobing = false;
}

void toggleLed() {
  clearLeds();
  
}

void clearLeds() {
  for (int i = 0; i < numLeds; i++){
    digitalWrite(ledPins[i], LOW);
  }
}
