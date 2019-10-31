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
  Serial.begin(115200);
}

void loop() {
  Serial.println(digitalRead(trig));
  
}
