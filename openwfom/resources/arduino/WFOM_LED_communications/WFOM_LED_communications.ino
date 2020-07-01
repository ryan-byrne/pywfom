#define greenLed  11
#define redLed    10
#define blueLed    9
#define limeLed    8
#define trig       13

// ledArray = 7,8,10,12
int ledArray[4] = {7,8,10,12};
String orderString = "BLGR";
float f, e;
String frm, ord, esp, msg;
char active;

void setup() {
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
    /*

    The main loop waits for a signal over the Serial Port.

    It then turns that signal into a message string.

    It checks if that string is an integer (controlLed) or not (strobeLed)

    */
    if (Serial.available() > 0){
      msg = "";
      while (Serial.available() > 0){
        char c = char(Serial.read());
        msg += c;
        delay(50);
      }
      Serial.println(msg.length());
    }
    if (msg.toInt()||msg=="0000"){
      controlLed(msg);
    }
    else {
      strobeLed(msg);
    }
    // msg = E0.0068ORGBLF50.70
    // strobeLed(msg);
}


void strobeLed(String msg){
  // Example Message : E0.0068ORGBLF50.70
  for (int i = 0; i < msg.length(); i++){
    char c = msg[i];
    if (c == 'E' || c == 'O' || c == 'F'){
     active = c;
     continue;
    }
    switch (active) {
      case 'E':
        esp += c;
        break;
      case 'O':
        ord += c;
        break;
      case 'F':
        frm += c;
        break;
    }
  }
  f = frm.toFloat();
  e = esp.toFloat();
  for (int i = 0; i < ord.length(); i++){
    digitalWrite(ledArray[orderString.indexOf(ord[i])], 1);
    delay(1/f*1000);
    digitalWrite(ledArray[orderString.indexOf(ord[i])], 0);
  }
}

void controlLed(String msg){
  // Example Message : 0100
  for (int i = 0; i < msg.length(); i++){
    digitalWrite(ledArray[i], int(msg[i])-48);
  }
}
