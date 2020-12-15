/*************************************************************************************************
* THREE_SOURCE_STROBE_LOGIC.pde and its associated files were created by:

* Matthew Bouchard*         mb2936@columbia.edu    917-359-2474  
* Ryan Sun 		    rs2878@columbia.edu    212-854-3852   
* Sasha Rayshubskiy	    ar3046@columbia.edu    212-854-3852		
* Elizabeth Hillman, PhD    eh2245@columbia.edu    917-207-0008

* Please contact Matthew Bouchard for any questions related to the 
* SPLASSH software.

* Copyright Laboratory for Functional Optical Imaging
* Department of Biomedical Engineering
* Columbia University

* THREE_SOURCE_STROBE_LOGIC.pde provides example strobe code for strobing
* up to three different, TTL logic driven illumination sources using an
* Arduino microcontroller. The code has been used on Arduino Diecimila
* microcontrollers and has been compiled using the Arduino development
* environment versions 16 and 22. Please see the SPLASSH manual for
* information on how to connect and operate the Arduino microcontroller
* in conjunction with the SPLASSH control software.
/*****************************************************************/


/***************************************************************
* Select the strobe TTL logic used by your illumination source. 
* Here, the macro LED_ON corresponds to the TTL signal level used 
* to turn the illumination source on while LED_OFF corresponds
* to the TTL signal level used to turn the illumination source off.
* These values are used to set the logic state of Arduino digital
* output pins
****************************************************************/
// L1 convention: Negative LED convention
//#define LED_ON LOW
//#define LED_OFF HIGH

// L2 convension: Positive LED convention
#define LED_ON HIGH
#define LED_OFF LOW
/*****************************************************************/

/******************************************************************
* Set the pin configuration for to match the pins where each illumination
* source strobe signal is to be output. The default settings were chosen 
* arbitrarily
*******************************************************************/
int LED1_pin = 8;
int LED2_pin = 10;
int LED3_pin = 12;
/*****************************************************************/

/******************************************************************
* Declare and initialize global variables. The volatile variables are
* used in Arduino interrupt functions (see 
http://www.arduino.cc/en/Reference/Volatile for more information, page
accessed on April 20, 2011)
*******************************************************************/
int StimDelay_pin = 5;
int LED_pin = -1;
volatile int incomingByte = -1;
volatile int controlthree = -1;
volatile int checkthree = -1;
volatile int firsttimeon = 1;
volatile int controltwo = -1;
volatile int checktwo = -1;
volatile int LED1_toggle_state = LED_OFF;
volatile int LED2_toggle_state = LED_OFF;
volatile int LED3_toggle_state = LED_OFF;
volatile int StimDelay = HIGH;
/*****************************************************************/


/******************************************************************
* Set up Arduino board for 3 digital outputs. Open serial port for
* communication between Arduino and SPLASSH control software
*******************************************************************/
void setup()
{
  // Initialize Digitial Output pins
  pinMode(LED1_pin, OUTPUT);
  pinMode(LED2_pin, OUTPUT);
  pinMode(LED3_pin, OUTPUT);
  pinMode(StimDelay_pin, OUTPUT); 
  
  // Set the initial states of the Digital Output pins high to turn off LEDs
  digitalWrite(LED1_pin, LED_OFF);
  digitalWrite(LED2_pin, LED_OFF);
  digitalWrite(LED3_pin, LED_OFF);
  digitalWrite(StimDelay_pin, LED_ON);

  // Open Serial port at 9600 BPS
  Serial.begin(9600);
}

/******************************************************************
* Within the Arduino's loop function, receive commands to set the
* illumination source strobe sequence, turn illumination sources on or
* off, and reset the strobe state variable. Return responses to SPLASSH
* control software to confirm proper operation.
*******************************************************************/
void loop()
{
  if (Serial.available() > 0) 
  {
    // read the incoming byte:
    incomingByte = Serial.read();

    // Choose operation
    // Disable interrupts
    if (incomingByte == 56) //8
    {
      digitalWrite(LED1_pin, LED_OFF);
      digitalWrite(LED2_pin, LED_OFF);
      digitalWrite(LED3_pin, LED_OFF);
      LED1_toggle_state = LED_OFF;
      LED2_toggle_state = LED_OFF;
      LED3_toggle_state = LED_OFF;
      
      detachInterrupt(0);
      detachInterrupt(1);
      
      Serial.print("Interrupts disabled"); 
    }
    
    // Enable interrupts for 1 LED
    else if ((incomingByte == 49)  || (incomingByte == 50) || (incomingByte == 51))  //1 or 2 or 3
    {
       digitalWrite(LED1_pin, LED_OFF);  
       digitalWrite(LED2_pin, LED_OFF);
       digitalWrite(LED3_pin, LED_OFF);
       
       switch(incomingByte)
       {
         case 49:
           LED_pin = LED1_pin;
           break;
         case 50:
           LED_pin = LED2_pin;
           break;
         case 51:
           LED_pin = LED3_pin;
           break;
       }
              
       attachInterrupt(0, turn_on_1_LED, RISING);
       attachInterrupt(1, turn_off_1_LED, FALLING);
       
       firsttimeon = 1;

       Serial.print("Interrupts enabled"); 
    }
    
    // Enable interrupts for 2 LEDs
    else if ((incomingByte == 65) || (incomingByte == 66) || (incomingByte == 67) || (incomingByte == 68) || (incomingByte == 69) || (incomingByte == 70))  //A, B, C, D, E, F
    {
      digitalWrite(LED1_pin, LED_OFF);
      digitalWrite(LED2_pin, LED_OFF);
      digitalWrite(LED3_pin, LED_OFF);     
      
      attachInterrupt(0, turn_on_2_LEDs, RISING);
      attachInterrupt(1, turn_off_2_LEDs, FALLING);
      
      checktwo = incomingByte;        
      firsttimeon = 1;
      
      Serial.print("Interrupts enabled");  
    }
    
    ///Enable interrupts for 3 LEDs
    else if ((incomingByte == 101) || (incomingByte == 102) || (incomingByte == 103) || (incomingByte == 104) || (incomingByte == 105) || (incomingByte == 106))
    {
      digitalWrite(LED1_pin, LED_OFF);
      digitalWrite(LED2_pin, LED_OFF);
      digitalWrite(LED3_pin, LED_OFF);
            
      attachInterrupt(0, turn_on_3_LEDs, RISING);
      attachInterrupt(1, turn_off_3_LEDs, FALLING);
      
      checkthree = incomingByte;
      
      firsttimeon=1;

      Serial.print("Interrupts Enabled");
    }
    
          
    // Toggle LED1
    else if (incomingByte == 53)  //5
    {
      if (LED1_toggle_state == LED_OFF)  
      {
        digitalWrite(LED1_pin, LED_ON);
        digitalWrite(LED2_pin, LED_OFF);
        digitalWrite(LED3_pin, LED_OFF);
        LED1_toggle_state = LED_ON;
      }
      else
      {
        digitalWrite(LED1_pin, LED_OFF);
        digitalWrite(LED2_pin, LED_OFF);
        digitalWrite(LED3_pin, LED_OFF);
        LED1_toggle_state = LED_OFF;
      }
      Serial.print("LED1 toggled");  
    }
    
    // Toggle LED2
    else if (incomingByte == 54) //6
    {
      if (LED2_toggle_state == LED_OFF) 
      {
        digitalWrite(LED1_pin, LED_OFF);
        digitalWrite(LED2_pin, LED_ON);
        digitalWrite(LED3_pin, LED_OFF);
        LED2_toggle_state = LED_ON;
      }
      else   
      {
        digitalWrite(LED1_pin, LED_OFF);
        digitalWrite(LED2_pin, LED_OFF);
        digitalWrite(LED3_pin, LED_OFF);
        LED2_toggle_state = LED_OFF;
      }
      Serial.print("LED2 toggled");    
    }
    
    // Toggle LED3
    else if (incomingByte == 55)  //7
    {
      if (LED3_toggle_state == LED_OFF) 
      {
        digitalWrite(LED1_pin, LED_OFF);
        digitalWrite(LED2_pin, LED_OFF);
        digitalWrite(LED3_pin, LED_ON);
        LED3_toggle_state = LED_ON;
      }
      else  
      {
        digitalWrite(LED1_pin, LED_OFF);
        digitalWrite(LED2_pin, LED_OFF);
        digitalWrite(LED3_pin, LED_OFF);
        LED3_toggle_state = LED_OFF;
      }
      Serial.print("LED3 toggled");      
    }
    
    else if(incomingByte == 48) //0
  {
    if (StimDelay == HIGH)
    {
      digitalWrite(StimDelay_pin, LOW);
      StimDelay = LOW;
    }
    else
    {
      digitalWrite(StimDelay_pin, HIGH);
      StimDelay = HIGH;
    }
    Serial.print("Stim Trigger Reset");      
  }    
  
    //Reset state variable  
    else if (incomingByte == 97)  //a
    { 
     firsttimeon = 1;
     Serial.print("State reset");
    }
    else
    {
      Serial.print("I received: ");
      Serial.println(incomingByte,DEC);
    }
    Serial.flush();
  }
  
}

// turn_on_1_LED interrupt function, executed when a rising edge is detected on pin2
void turn_on_1_LED()  
{
    digitalWrite(LED_pin, LED_ON);
}

// turn_off_1_LED interrupt function, executed when a falling edge is detected on pin 3
void turn_off_1_LED()  
{
    digitalWrite(LED_pin, LED_OFF);
}

// turn_on_2_LEDs interrupt function, executed when a rising edge is detected on pin 2
void turn_on_2_LEDs()  
{
  if (firsttimeon == 1)
  {
    switch(checktwo)
    {
      case 65:
        controltwo = 1;
        break;
      case 66:
        controltwo = 1;
        break;
      case 67:
        controltwo = 2;
        break;
      case 68:
        controltwo = 2;
        break;
      case 69:
        controltwo = 3;
        break;
      case 70:
        controltwo = 3;
        break;
    }
 
   firsttimeon = 0;
 }
    
 if(controltwo == 1)
   {
     digitalWrite(LED1_pin, LED_ON);
   }

 if(controltwo == 2)
   {
     digitalWrite(LED2_pin, LED_ON);
   }
  
 if(controltwo == 3)
   {
     digitalWrite(LED3_pin, LED_ON);
   }
}

// turn_off_2_LEDs interrupt function, executed when a falling edge is detected on pin 3
void turn_off_2_LEDs() 
{
  switch(checktwo)
  {
    case 65:
      if(controltwo == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controltwo++;
        break;
      }
      if(controltwo == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controltwo = 1;
        break;
      }
   case 66:
     if(controltwo == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controltwo = 3;
        break;
      }
      if(controltwo == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controltwo = 1;
        break;
      }
   case 67:
     if(controltwo == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controltwo = 1;
        break;
      }
     if(controltwo == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controltwo = 2;
        break;
      }
   case 68:
     if(controltwo == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controltwo = 3;
        break;
      }
     if(controltwo == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controltwo = 2;
        break;
      }
   case 69:
     if(controltwo == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controltwo = 1;
        break;
      }
     if(controltwo == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controltwo = 3;
        break;
      }
   case 70:
     if(controltwo == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controltwo = 3;
        break;
      }
     if(controltwo == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controltwo = 2;
        break;
      }
  }
}

//turn_on_3_LEDs interrupt function, executed when a rising edge is detected on pin2
void turn_on_3_LEDs()
{
  if (firsttimeon == 1)
  {
    switch(checkthree)
    {
      case 101:
        controlthree = 1;
        break;
      case 102:
        controlthree = 1;
        break;
      case 103:
        controlthree = 2;
        break;
      case 104:
        controlthree = 2;
        break;
      case 105:
        controlthree = 3;
        break;
      case 106:
        controlthree = 3;
        break;
    }

    firsttimeon = 0;
  }
  
  if (controlthree == 1)
    {
    digitalWrite(LED1_pin, LED_ON);
    } 

  if (controlthree == 2)
    {
    digitalWrite(LED2_pin, LED_ON);
    }

  if (controlthree == 3)
    {
    digitalWrite(LED3_pin, LED_ON);
    } 
}
  

//turn_off_3_LEDs interrupt function, executed when a falling edge is detected on pin3
void turn_off_3_LEDs()
{
  switch(checkthree)
  {
    case 101:
      if(controlthree == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controlthree = 2;
        break;
      }
      if(controlthree == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controlthree = 3;
        break;
      }
      if(controlthree == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controlthree = 1;
        break;
      }
   case 102:
     if(controlthree == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controlthree = 3;
        break;
      }
      if(controlthree == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controlthree = 1;
        break;
      }
      if(controlthree == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controlthree = 2;
        break;
      }
   case 103:
     if(controlthree == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controlthree = 3;
        break;
      }
      if(controlthree == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controlthree = 1;
        break;
      }
      if(controlthree == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controlthree = 2;
        break;
      }
    case 104:
      if(controlthree == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controlthree = 2;
        break;
      }
      if(controlthree == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controlthree = 3;
        break;
      }
      if(controlthree == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controlthree = 1;
        break;
      }
    case 105:
      if(controlthree == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controlthree = 2;
        break;
      }
      if(controlthree == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controlthree = 3;
        break;
      }
      if(controlthree == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controlthree = 1;
        break;
      }
    case 106:
      if(controlthree == 1)
      {
        digitalWrite(LED1_pin, LED_OFF);
        controlthree = 3;
        break;
      }
      if(controlthree == 2)
      {
        digitalWrite(LED2_pin, LED_OFF);
        controlthree = 1;
        break;
      }
      if(controlthree == 3)
      {
        digitalWrite(LED3_pin, LED_OFF);
        controlthree = 2;
        break;
      }
  }
}
