#include "SmartStepper.h"

#define M1_PUL 34
#define M1_ENB 36
#define M1_DIR 38

#define M2_PUL 35
#define M2_ENB 37
#define M2_DIR 39

#define BAUD           115200
#define MAX_BUF        64  

SmartStepper stepper1(M1_PUL,M1_DIR);
SmartStepper stepper2(M2_PUL,M2_DIR);

// Global Variables
int buffer[MAX_BUF];
int buffer_pos;
bool startbit = false;
char mode_abs=1;
bool flag = false;
int s1_count = 0;
int s2_count = 0;

// put your setup code here, to run once:
void setup() {
	// Open Serial Port
	Serial.begin(BAUD);

	// stepper1.setPeriod(800);
	// stepper2.setPeriod(1000);

	// Set up Motor Pin Modes
	pinMode(M1_ENB,OUTPUT);
	pinMode(M1_DIR,OUTPUT);
	pinMode(M1_PUL,OUTPUT);

	pinMode(M2_ENB,OUTPUT);
	pinMode(M2_DIR,OUTPUT);
	pinMode(M2_PUL,OUTPUT);

	// Set up Enables
	digitalWrite(M1_ENB,LOW);
	digitalWrite(M2_ENB,LOW);
}

// put your main code here, to run repeatedly:
void loop() {
	if(!stepper1.movementRequired() && !stepper2.movementRequired() && Serial.available()){
                Serial.println("?");
		int c = Serial.read();

		if(c == int(0xFE)){
			startbit = true;
		}

		if(startbit){
			if(buffer_pos < MAX_BUF) buffer[buffer_pos++]=c;
    		
  		if(buffer_pos == MAX_BUF && c != int(0xFE)){
  			buffer_pos = 0;
  			startbit = false;
  		} 
		}

		if(startbit && c == int(0xEF)){
			startbit = false;
			buffer_pos = 0;
			processBuffer();
		}
	}

	if(flag){
            if(s1_count < 800){
               Serial.println("On the Move 1!");
	       stepper1.run(); 
                s1_count++;
            }
	}

	if(flag){
              if(s1_count < 800){
                 Serial.println("On the Move 2!");
	         stepper2.run();
                 s2_count++;
              }
	}
}

void move(SmartStepper stepper, long new_pos, bool moveAbsolute, unsigned long period){
        Serial.println("Move Methods...");
	int current_pos = stepper.getCurrentPos();

	if(!moveAbsolute){
		new_pos += current_pos;
	} 

	int change_pos = new_pos - current_pos;

	int pos_direction = change_pos>0?1:-1;

	if(pos_direction > 0){
  	stepper.setDirection(HIGH);
  }else {
  	stepper.setDirection(LOW);
  }

  int abs_pos = abs(change_pos);

  Serial.println("More Methods...");
  Serial.println(abs_pos);
  stepper.setDesiredPos(abs_pos);
  stepper.setPeriod(period);
}

void processBuffer(){
        flag = true;
	// Read and Interpret from Buffer
        Serial.println("PROCESS BUFFER!!");
	// Set Stepper to move
	move(stepper1, 1600, 1, 800);
	move(stepper2, 1600, 1, 800);
}




