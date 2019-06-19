const int greenLed = 11;
const int redLed = 10;
const int yellowLed = 9;

void setup() {
  pinMode(greenLed, OUTPUT);
  pinMode(redLed, OUTPUT);
  pinMode(yellowLed, OUTPUT);
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
}

void loop() {
  if (Serial.available()>0){
    byte i = Serial.read();
    if (i > 0){
      digitalWrite(greenLed, HIGH);
    }
    else{
      digitalWrite(greenLed, LOW);
    }
  }
  
}
