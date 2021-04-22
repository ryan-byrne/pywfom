#ifndef PyWFOM_h
#define PyWFOM_h

#include <stdlib.h>
#include <Arduino.h>

class PyWFOM {

  private:

    // Variables for Serial
    char _incomingChar;
    int _iidx;
    // Receiving Message
    char _incomingMessage[36];
    boolean _receivingMessage;
    // Receiving Command
    char _incomingCommand[36];
    boolean _receivingCommand;
    // Message to be sent back
    char _outgoingMessage[36];
    int _oidx;
    // Pin Recorder
    char _pinChars[3];
    int _pidx;
    // Stored pin variables
    int _triggerPin;
    int _ledPins[10];
    int _daqPins[10];
    int _stimPins[4];
    // Misc
    char _firmwareVersion[10] = "0.0.1";
    int _triggerMode;

  public:

    PyWFOM ();
    void Init();
    void Run();
    void readMessage();
    void readCommand();
    void setTriggerPin();
    void setPins( int *pins, int mode);
    void runCommands();
    void sendMessage();
    void controlStim();
    void controlLeds();

};

#endif
