#ifndef SmartStepper_h
#define SmartStepper_h

#include <Arduino.h>

class SmartStepper {
public:
	// Smart Stepper Constructor
	SmartStepper(unsigned int pin_pulse,unsigned int pin_dir);
	
	// Methods for Stepper Movement Routines
	boolean run();
	boolean movementRequired();

	// Setters for Stepper Motor Attributes
	void setPeriod(long period);
	void setMinWidth(unsigned int minWidth);
	void setDesiredPos(long desiredPos, bool relative = false);
	
  void resetCurrentPos();

	// Getters for Stepper Motor Attributes
	long getCurrentPos();

protected:
	// For Doing other Wierd Stuff
	volatile uint8_t* getPort(unsigned int pin);
	uint8_t getPinMask(unsigned int pin);

	// For Pulling Digital Pins High and Low
	uint8_t getBits(volatile uint8_t *port, uint8_t mask);
	void setBits(volatile uint8_t *port, uint8_t mask);
	void resetBits(volatile uint8_t *port, uint8_t mask);

private:
	//Internal Helper Functions
	void setDirection(bool desiredDirection);
	
	// Info for setting registers
	unsigned int _pin[4];
	volatile uint8_t* _port[4];
	unsigned int _pinMask[4];
	unsigned int _pinMask_inv[4];

	// Stepper Motor Direction
	bool _dirValue;

  // Current and Desired Pos of Stepper Motor
	long _currentPos;
	long _desiredPos;

	// Values for setting the attributes of the pulse signal
	unsigned long _prevStepTime;
	unsigned long _period;
	unsigned int _minWidth;
	bool _loopPeriod;
};

#endif
