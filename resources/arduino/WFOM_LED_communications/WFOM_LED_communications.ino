const int greenLed = 11;
const int redLed = 10;
const int blueLed = 9;
const int limeLed = 8;
int ledArray[4] = {redLed,blueLed,greenLed,limeLed};
int i;

void setup() {
  for (int i = 0; i<4 ; i++){
    pinMode(ledArray[i], OUTPUT);
  }
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
}

void loop() {
  i = 0;
  while (Serial.available() > 0){
    int recieved = Serial.read();
    digitalWrite(ledArray[i], recieved - 48);
    i++;
    delayMicroseconds(100);
  }
}
