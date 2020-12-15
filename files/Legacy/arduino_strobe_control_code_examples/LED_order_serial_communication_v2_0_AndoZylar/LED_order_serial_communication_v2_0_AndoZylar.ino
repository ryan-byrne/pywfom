/***************************************************************
 * This code allows one to toggle and strobe  TTL logic driven 
 * illumination sources using anArduino microcontroller 
 * (up to a maximum of 9) in any order.
 ****************************************************************/

/***************************************************************
 * Select the strobe TTL logic used by your illumination source. 
 * Here, the macro LED_ON corresponds to the TTL signal level used 
 * to turn the illumination source on while LED_OFF corresponds
 * to the TTL signal level used to turn the illumination source off.
 * These values are used to set the logic state of Arduino digital
 * output pins
 ****************************************************************/
#define LED_ON HIGH
#define LED_OFF LOW

//Define how many sources will be strobed
#define LENGTH_LED_ARRAY 4

//Global variables
volatile int incoming_value;
int *LED_order = NULL;
volatile int LED_array[] = {13,11,9,8};
volatile int Exposure_Output_pin=5;
volatile int Stim_Delay_pin=7;
volatile int Stim_Delay_state=0;
volatile int ledToggleIndex = 0;
volatile int numberOfElements = 0;
volatile int nextLED=0;
volatile int start_delay=1;
volatile int ts=-1;

void setup()
{
  Serial.begin(9600);
  for (int i=0; i<4; i++)
  {
    pinMode(LED_array[i],OUTPUT);
    digitalWrite(LED_array[i],LED_OFF);
  }
  pinMode(Stim_Delay_pin,INPUT);
  pinMode(Exposure_Output_pin,OUTPUT);
  digitalWrite(Exposure_Output_pin,LED_OFF);

}

void loop()
{
  while (Serial.available()>0)
  {
    incoming_value = Serial.read();
    switch (incoming_value)
    {
    case 99: // c
      detachInterrupt(0);
      detachInterrupt(1);
      turn_off_all_LEDs();
      if (NULL != LED_order)
      {
        free(LED_order);
        LED_order = NULL;
      }
      Serial.print("Interrupts disabled"); 
      break;

    case 116:  // t
      // Turn off all LEDs first
      //Serial.println("Toggle all LEDs OFF");
      turn_off_all_LEDs();

      delay(10);
      //Serial.println("Toggle next LED ON");
      ledToggleIndex = Serial.read() - 49;
      //Serial.println(LED_array[ledToggleIndex], DEC);
      digitalWrite(LED_array[ledToggleIndex], LED_ON);
      Serial.print(ledToggleIndex+1,DEC);   
      break;

    case 120: // x
      Serial.println("Toggle all LEDs OFF");
      turn_off_all_LEDs();
      break;

    case 115: // s
      delay(10);
      // read number of available bytes
      numberOfElements = Serial.available();

      // allocate array using malloc and initalize all elements to 0
      LED_order = (int *) malloc(numberOfElements * sizeof(int));
      for (int counter = 0; counter < numberOfElements; counter++)   {
        LED_order[counter] = 0;
      }

      // Read in strobe order
      for (int counter = 0; counter < numberOfElements; counter++)   {
        LED_order[counter] = Serial.read() - 49;
      }

      //Serial.println("LED_order is:");
      //for (int counter = 0; counter < numberOfElements; counter++)   {
      //  Serial.println(LED_order[counter], DEC);
      //}

      //Serial.println("Pin order");
      //for (int counter = 0; counter < numberOfElements; counter++)   {
      //  Serial.println(LED_array[LED_order[counter]], DEC);
      //}

      nextLED=0;
      //digitalWrite(Exposure_Output_pin,LED_OFF);
      digitalWrite(0,LOW);
      digitalWrite(1,LOW);
      start_delay=1;
      attachInterrupt(0, strobe_on_LEDs, RISING);
      attachInterrupt(1, strobe_off_LEDs, FALLING);
      Serial.print("Interrupts enabled");
      break;  

    case 114: //r
      //digitalWrite(Stim_Delay_pin, LOW);
      Serial.print("Stim Trigger Reset");  
      break;

    case 82: //R
      //digitalWrite(Stim_Delay_pin, HIGH);
      Serial.print("Stim Trigger Reset");  
      break;

    case 97: //a
      Serial.print("State reset");
      nextLED=0;
      break;

    case 102: //f
      Serial.flush();
      Serial.println("Flush");
      break;

    case 77: //M (legacy from Matt's code to check comm status)
      Serial.println("I'm ready to get the data");
      break;

    case 100: //d -- Stim Delay read
      Stim_Delay_state=digitalRead(Stim_Delay_pin);
      if (Stim_Delay_state==1)
      {
        Serial.print("Ready");
      }
      else
      {
        Serial.print("Wait");
      }
      break;
    }
  }
}


void strobe_on_LEDs()
{
  Serial.println(millis()-ts);
  if (start_delay==1){
    sei();
    delayMicroseconds(5000);
    start_delay=0;
  }
  //Serial.println(LED_array[LED_order[nextLED]]);
  digitalWrite(LED_array[LED_order[nextLED]], LED_ON);
  digitalWrite(Exposure_Output_pin,LED_ON);
  ts=millis();
}


void strobe_off_LEDs()
{
  digitalWrite(LED_array[LED_order[nextLED]], LED_OFF);
  digitalWrite(Exposure_Output_pin,LED_OFF);
  if (nextLED < (numberOfElements - 1))
  {
    nextLED++;
  }
  else if (nextLED == (numberOfElements - 1))
  {
    nextLED = 0;
  }
}

void turn_off_all_LEDs()
{
  for (int i=0; i < LENGTH_LED_ARRAY; i++)
  {
    digitalWrite(LED_array[i], LED_OFF);
  }
  digitalWrite(Exposure_Output_pin,LED_OFF);
}

