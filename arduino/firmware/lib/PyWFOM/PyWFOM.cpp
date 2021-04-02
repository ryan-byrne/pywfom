#include "PyWFOM.h"
#include <Arduino.h>

PyWFOM::PyWFOM() {
  _iidx = 0;
  _oidx = 0;
  _pidx = 0;
  _triggerMode = 0;
}

void PyWFOM::Init() {
  Serial.begin(115200);
}

void PyWFOM::Run( ) {

  // Check if a message is available
  while (Serial.available() > 0){

    _incomingChar = Serial.read();
    // Only record values between carrots (<>)
    switch (_incomingChar) {
      case '<':
        _receivingMessage = true;
        _iidx=0;
        break;
      case '>':
        _receivingMessage = false;
        break;
      case '(':
        _receivingCommand = true;
        _iidx=0;
        break;
      case ')':
        _receivingCommand = false;
        break;
      default:
        if (_receivingMessage) { _incomingMessage[_iidx++] = _incomingChar; }
        else if (_receivingCommand) {_incomingCommand[_iidx++] = _incomingChar;}
    }

  }

  // If there is a new message, and it is complete, interpret it
  if (strlen(_incomingMessage) > 0 && !_receivingMessage) {readMessage();}
  // If there is a new command, and it is complete, interpret it
  else if (strlen(_incomingCommand) > 0 && !_receivingCommand){readCommand();}

  if (_triggerMode == 1) {
    // Continously return message
    sendMessage();
  } else if (_triggerMode == 2) {
    // Only return message when trigger pin is high
    while(digitalRead(_triggerPin)){}
    sendMessage();
    while(digitalRead(!_triggerPin)){}
  }
  // _triggermode == 0 will only return messages when prompted

}

void PyWFOM::readMessage() {

  switch (_incomingMessage[0]) {
    case 'f':
      Serial.println(_firmwareVersion);
      break;
    case 't':
      setTriggerPin();
      break;
    case 'm':
      _triggerMode = _incomingMessage[1];
      break;
    case 'l':
      setPins(_ledPins, OUTPUT);
      break;
    case 'd':
      setPins(_daqPins, INPUT);
      break;
    case 's':
      setPins(_stimPins, OUTPUT);
      break;

  }

  // Clear the message
  _incomingMessage[0] = '\0';
}

void PyWFOM::readCommand() {

  switch (_incomingCommand[0]) {
    case 'l':
      controlLeds();
      break;
    case 's':
      controlStim();
      break;
  }

  _incomingCommand[0] = '\0';
}

void PyWFOM::setTriggerPin() {
  char _trigChars[2] = {_incomingMessage[1], _incomingMessage[2]};
  _triggerPin = atoi(_trigChars);
}

void PyWFOM::setPins( int *pins, int mode) {

  _pidx = 0;
  int _lidx = 0;

  for (int i=1; i<sizeof(_incomingMessage); i++) {
    if ( _incomingMessage[i] == ',' ) {
      _pinChars[_pidx++] = '\0';
      pins[_lidx++] = atoi(_pinChars);
      pinMode(atoi(_pinChars), mode);
      _pidx = 0;
      _pinChars[0] = '\0';
    } else {
      _pinChars[_pidx++] = _incomingMessage[i];
    }
  }

}

void PyWFOM::controlLeds(){
  for (int i=1;i<sizeof(_incomingCommand);i++){
    digitalWrite(_ledPins[i], atoi(_incomingCommand[i]));
  }
}

void PyWFOM::controlStim(){}

void PyWFOM::sendMessage() {}
