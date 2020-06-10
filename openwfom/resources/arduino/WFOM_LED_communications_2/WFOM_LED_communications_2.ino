#define greenLed    7
#define redLed      8
#define blueLed     12
#define limeLed     10
#define trig        3

int ledArray[4] = {greenLed, redLed, blueLed, limeLed};
String orderString = "RLGB";
bool last;
String msg, ord;
bool strobing;
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
    // Recieving new message over the Serial Port
    // Creating blank message
    msg = "";
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
      delay(50);
    }
    // Checking to see if the message was an LED test (1's and 0's), if not the order is set
    if (msg.toInt()||msg=="0000"){
      // Control Particular LED's
      controlLed(msg);
    }
    else if (msg == "S"){
      // Turn strobing on
      strobing = true;
    }
    else if (msg == "s"){
      // Turn strobing off
      strobing = false;
      controlLed("0000");
    }
    else{
      // Set Strobe Order
      ord = msg;
      Serial.println(ord);
    }
  }
  // Waits until the order is set, and the shutter is open to begin strobing
  if ((digitalRead(trig))&&(ord.length()>0)&&(strobing)){
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
