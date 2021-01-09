char incomingChar;
char receivedChars[32];
boolean msgComplete = false;
boolean receivingMsg = false;
int currentLed = 0;
int numLeds = 0;
int numDaq = 0;
int ledPins[10];
int stimPins[10];
int daqPins[10];
int trigPin;
char msg[32];
int midx = 0;
char pin[2];
char val[3];
boolean strobing = false;

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
      case 'c':
        clearLeds();
        break;
      case 't':
        trigPin = int(receivedChars[1]);
    }
    
    msgComplete = false;
  }
}

void returnData(){

  /*
   * Message Format: s,d_5:256,
   * A = strobing (s or S)
   * B = DAQ
   */
   
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

void updateLedPins(){

  char c;
  char pin[4];
  int idx = 0;
  numLeds = 0;
  
  for ( int i=1; i<sizeof(receivedChars); i++ ) {
    
    c = receivedChars[i];
    
    if (int(c) == 0){
      continue;
    }
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

  char c;
  char pin[4];
  int idx = 0;
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
  trigPin;
  int ledPins[] = {};
  int stimPins[] = {};
  String msg;
  currentLed = 0;
  strobing = false;
}

void clearLeds() {
  for (int i = 0; i < numLeds; i++){
    digitalWrite(ledPins[i], LOW);
  }
}
