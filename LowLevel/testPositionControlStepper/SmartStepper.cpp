#include "SmartStepper.h"

// Constructor to the Smart Stepper Motor Class
// Recieves the pin to pulse on and the direction pin 
// of a given stepper motor
SmartStepper::SmartStepper(unsigned int pin_pulse,unsigned int pin_dir){
	// Store pin values
  _pin[0]= pin_pulse;
	_pin[1]= pin_dir;

  // Determine the port and pin mask for each pin for setting registers later
  for(int i=0;i<2;i++){
    _port[i] = getPort(_pin[i]);
    _pinMask[i] = getPinMask(_pin[i]);
    _pinMask_inv[i] = ~_pinMask[i];
  }

  // Initialize the current and desired positon 
  _currentPos = 0;
  _desiredPos = 0;

  // Initialize the direction of the motor
  _dirValue = HIGH;

  // Time between consecutive high edges in the signal
  _period = 1000;

  // Size of the square wave (duration held high)
  _minWidth = 10;
  
  // Natural Delay from Atmega (the amount it takes to loop in itself) 
  _loopPeriod = 20;
  
  // Store the last time the motor was stepped
  _prevStepTime = 0;
}
	
// Main Method for Pulsing Stepper Motors
boolean SmartStepper::run(){
        Serial.println("RUN!");
	// Get the current time 
	unsigned long currentTime = micros();

  // Find the change in time
	unsigned long delta_t = currentTime -_prevStepTime;
	
  // ?
	if(getBits(_port[0],_pinMask[0])){
    // Then if the change in time is greater than the min width of the square wave
		if(delta_t>_minWidth){
      // Pull Motor Pulse Pin Low
      resetBits(_port[0],_pinMask_inv[0]);
		}
	}
  // If the change in time is greater than the signal period minus the natural delay of the Atmega2560
	else if(delta_t>(_period-(_loopPeriod))){
    // Pull Motor Pulse Pin High
    setBits(_port[0],_pinMask[0]);

    // Increment the current position
    _currentPos++;
    
    _desiredPos++;

    // Record latest time
    _prevStepTime = micros();
	}
}

// Set the period of the stepper motor pulse signal
void SmartStepper::setPeriod(long per){
  Serial.println("Set Period...");
  _period = per;
}

// Get the current position of the stepper motor (the where we are now)
long SmartStepper::getCurrentPos(){
  return _currentPos;
}

// Set the Desired Position of the stepper motor (the where we want to go)
void SmartStepper::setDesiredPos(long desPos){
  Serial.println("Set Desired Pos...");
  //this->_desiredPos = desPos;
  _desiredPos = desPos;
  Serial.println(_desiredPos);
  Serial.println(_currentPos);
}

// If the current position is the desired position no movement is required
boolean SmartStepper::movementRequired(){
  Serial.print(_currentPos);
  Serial.print(" ");
  Serial.print(_desiredPos);
  Serial.print(" ");
  Serial.print(_period);
  Serial.print(" ");
  Serial.println(_currentPos != _desiredPos);
  return (_currentPos != _desiredPos);
}

// Set the direction of the Stepper Motor itself
void SmartStepper::setDirection(bool desiredDir){
  _dirValue = desiredDir;
  if(_dirValue){
    // Pull direction High
    setBits(_port[1],_pinMask_inv[1]);
  } else {
    // Pull Direction Low
    resetBits(_port[1],_pinMask_inv[1]);
  }
}

// Get Port Finds the port for the given pin
volatile uint8_t* SmartStepper::getPort(unsigned int pin){
  if(pin>=22&&pin<=29)
    return &PORTA;
  else if(pin>=30&&pin<=37)
    return &PORTC;
  else if(pin>=42&&pin<=49)
    return &PORTL;
  else
    return 0;
}

// Get Port Finds the pin mask for the given pin
uint8_t SmartStepper::getPinMask(unsigned int pin){
  if(pin==22||pin==37||pin==49)
    return 0x01;
  if(pin==23||pin==36||pin==48)
    return 0x02;
  if(pin==24||pin==35||pin==47)
    return 0x04;
  if(pin==25||pin==34||pin==46)
    return 0x08;
  if(pin==26||pin==33||pin==45)
    return 0x10;
  if(pin==27||pin==32||pin==44)
    return 0x20;
  if(pin==28||pin==31||pin==43)
    return 0x40;
  if(pin==29||pin==30||pin==42)
    return 0x80;
}

// ?????
uint8_t SmartStepper::getBits(volatile uint8_t *port, uint8_t mask){
  return *port & mask;
}

// Pulls Motors High
void SmartStepper::setBits(volatile uint8_t *port, uint8_t mask){
  *port |= mask;
}

// Pulls Motors Low
void SmartStepper::resetBits(volatile uint8_t *port, uint8_t mask){
  *port &= mask;
}

