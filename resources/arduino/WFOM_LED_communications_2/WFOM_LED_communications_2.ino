#define greenLed    8
#define redLed      10
#define blueLed     7
#define limeLed     12
#define trig        3

int ledArray[4] = {greenLed, redLed, blueLed, limeLed};
String orderString = "GRBL";
bool last;
String msg, ord;
int led, incomingByte;

void setup() {
  pinMode(trig, INPUT);
  for (int i = 0; i<4 ; i++){
    pinMode(ledArray[i], OUTPUT);
    digitalWrite(ledArray[i], 0);
  }
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
}

void loop() {
  if (Serial.available() > 0){
    msg = "";
    while (Serial.available() > 0){
      int c = Serial.read();
      if (c<50){
        continue;
      }
      else{
        msg += char(c);
      }
      delay(50);
    }
    if (msg.toInt()||msg=="0000"){
      controlLed(msg);
    }
    else{
      ord = msg;
      Serial.println(ord);
    }
  }
  if ((digitalRead(trig))&&(ord.length()>0)){
    // Sensor is exposed
    if (last == false){
      // New exposure
      digitalWrite(ledArray[orderString.indexOf(ord[led])], 0);
      led = (led+1) % ord.length();
      digitalWrite(ledArray[orderString.indexOf(ord[led])], 1);
    }
    last = true;
  }
  else{
    // Sensor is not exposing row one
    last = false;
  }
}

void controlLed(String msg){
  // Example Message : 0100
  for (int i = 0; i < msg.length(); i++){
    digitalWrite(ledArray[i], int(msg[i])-48);
  }
}
