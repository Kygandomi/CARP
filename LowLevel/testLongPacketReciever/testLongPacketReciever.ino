// Painting Robot MQP 
// Low Level Code V1
#include <PID_v1.h>

#define BAUD           115200
#define MAX_BUF        64  
#define MAX_COMMANDS   1000

#define SERIAL_ELEMENT_LEN 10

#define F1 52
#define F2 53
#define POT A1
#define pwm 12

#define M1_PUL 34
#define M1_ENB 36
#define M1_DIR 38

#define M2_PUL 35
#define M2_ENB 37
#define M2_DIR 39

// Global Variables
int buffer[MAX_BUF];
int buffer_pos;
bool startbit = false;

// Motor Step Definitions and Start Times
long m1_steps = 0;
int m1_step_time = 0;
unsigned long m1_start_time = 0;

long m2_steps = 0;
int m2_step_time = 0;
unsigned long m2_start_time = 0;

// Fergelli Controller Variables
double Setpoint, Input, Output;

// Current position of gantry in M1/M2 space
long current_m1 = 0;
long current_m2 = 0;
long current_f = 0;

//Define the aggressive and conservative Tuning Parameters
double aggKp=1, aggKi=0, aggKd=0;
double consKp=1, consKi=0.05, consKd=0.25;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);

// Command Structure
typedef struct{
  long m1_steps;
  long m2_steps;
  
  boolean m1_dir;
  boolean m2_dir;
  
  long m1_step_time;
  long m2_step_time;
    
  int fergelli_pos;
  
} command;

// For Command Buffer
int current_command_index = 0;
int length_command = 0;
command command_list[MAX_COMMANDS];

void setup_motors() {
    // Set up Pin Modes
    pinMode(F1,OUTPUT);
    pinMode(F2,OUTPUT);
    
    pinMode(M1_ENB,OUTPUT);
    pinMode(M1_DIR,OUTPUT);
    pinMode(M1_PUL,OUTPUT);

    pinMode(M2_ENB,OUTPUT);
    pinMode(M2_DIR,OUTPUT);
    pinMode(M2_PUL,OUTPUT);

    // Set up Enables
    digitalWrite(M1_ENB,LOW);
    digitalWrite(M2_ENB,LOW);
    
    digitalWrite(M1_DIR,HIGH);
    digitalWrite(M2_DIR,HIGH);
}

void setup(){
  // Open Serial Port
  Serial.begin(BAUD);
  
  // Set up Motors
  setup_motors();
  
  // Set output limits 
  myPID.SetOutputLimits(-255,255);
  
  // Initial Fergelli Setpoint
  Setpoint = 700;
  
  // Turn on PID
  myPID.SetMode(AUTOMATIC);
  delay(1000);
}


void loop(){
  Serial.println("loop");
        if(current_command_index >= length_command && !Serial.available()){
//            Serial.write(0xFE);
//            Serial.write(0x00);
//            Serial.write(0xEF);
        }
  
	else if(current_command_index >= length_command && Serial.available()){
//		int c = Serial.read();
//
//		if(c == int(0xFE)){
//			startbit = true;
//		}
//
//		if(startbit){
//			if(buffer_pos < MAX_BUF) buffer[buffer_pos++]=c;
//    		
//      		        if(buffer_pos == MAX_BUF && c != int(0xFE)){
//      			    buffer_pos = 0;
//      			    startbit = false;
//      		        } 
//		}
//
//		if(startbit && c == int(0xEF)){
//			startbit = false;
//			processBuffer();
//                        buffer_pos = 0;
//		}
	} 

        //move to position
        else if(current_command_index==-1){
            startCommand();
        }
        else{
          if(run()){
             startCommand();
          }
        }
        
       runFergelli();
}

void forwardKinematics(long delta_x, long delta_y, boolean* m1_dir, boolean* m2_dir, long* m1_steps, long* m2_steps){
	
        float mag = sqrt(pow(delta_x, 2) + pow(delta_y, 2));
	float angle =atan2(delta_y, delta_x); 

	float s1 = mag*sin(angle - 0.785398);
	float s2 = mag*cos(angle - 0.785398);

	if(s1 < 0)
	  *m1_dir = true;
	else
  	  *m1_dir = false;
	if(s2 < 0)
	  *m2_dir = true;
	else
	  *m2_dir = false;

	*m1_steps = long(abs(s1));
	*m2_steps = long(abs(s2));
}

void startCommand(){
  current_command_index++;
  Serial.println(current_command_index);
//  m1_steps = command_list[current_command_index].m1_steps;
//  m2_steps = command_list[current_command_index].m2_steps;
//          
//  m1_step_time = command_list[current_command_index].m1_step_time;
//  m2_step_time = command_list[current_command_index].m2_step_time;
//  
//  boolean m1_dir = command_list[current_command_index].m1_dir;
//  boolean m2_dir = command_list[current_command_index].m2_dir;
//  
//  Setpoint = command_list[current_command_index].fergelli_pos;
//  
//  current_m1 += command_list[current_command_index].m1_steps*(m1_dir ? -1 : 1);
//  current_m2 += command_list[current_command_index].m2_steps*(m2_dir ? -1 : 1);
//  current_f = command_list[current_command_index].fergelli_pos;
//  
//  // Set M1 Direction
//  if(m1_dir){
//    PORTD |= _BV(PD7);
//  } else {
//    PORTD &= ~_BV(PD7);
//  }
//          
//  // Set M2 Direction
//  if(m2_dir){
//    PORTG |= _BV(PG2);
//   } else {
//    PORTG &= ~_BV(PG2);
//   }
 
}

boolean run(){
   if(m1_steps == 0 && m2_steps == 0){
     return true;
   } 
   
   else {     
     if(m1_steps != 0){
	if(micros() - m1_start_time > (m1_step_time - 20) ){
		PORTC |= _BV(PC3);
		m1_steps--;
		m1_start_time = micros();
	}

        if(micros() - m1_start_time > 1 ){
		PORTC &= ~_BV(PC3);
        }
      }
  
      if(m2_steps != 0){
  	if(micros() - m2_start_time > m2_step_time){
  		PORTC |= _BV(PC2);
  		m2_steps--;
  		m2_start_time = micros();
  	}
  
          if(micros() - m2_start_time > 1 ){
  		PORTC &= ~_BV(PC2);
  	}
      }
     
    return false;   
   }
}

void runFergelli(){
  
 // Figure out where to go and how to move
    Input = analogRead(POT);
    current_f = Input;
        
    double gap = abs(Setpoint-Input); //distance away from setpoint
    if(gap<10)
    {  //we're close to setpoint, use conservative tuning parameters
        myPID.SetTunings(consKp, consKi, consKd);
    }
    else
    {
      //we're far from setpoint, use aggressive tuning parameters
      myPID.SetTunings(aggKp, aggKi, aggKd);
     }
        
      // Compute PID
      myPID.Compute();
        
      // Set Direction of Fergelli
      if(Output == 0){
         digitalWrite(F1, LOW);
         digitalWrite(F2, LOW);
         analogWrite(pwm, Output); 
       } else if(Output < 0){
         digitalWrite(F1, HIGH);
         digitalWrite(F2, LOW); 
         analogWrite(pwm, -1*Output);
        } else {
         digitalWrite(F1, LOW);
         digitalWrite(F2, HIGH);
         analogWrite(pwm, Output);
        } 
  
}

void processBuffer(){
     
  long sim_m1 = current_m1;
  long sim_m2 = current_m2;
  long sim_f = current_f;
  int sim_command_index = 0;
  
  for(int i=1; i<buffer_pos; i+=SERIAL_ELEMENT_LEN){
    if(i+SERIAL_ELEMENT_LEN < buffer_pos){
      long x = (buffer[i] << 8) + buffer[i+1];
      long y = (buffer[i+2] << 8) + buffer[i+3];
      boolean xy_abs_flag = buffer[i+4];
      
      long z = (buffer[i+5] << 8) + buffer[i+6];
      boolean z_abs_flag = buffer[i+7];
      
      long min_step_time = (buffer[i+8] << 8) + buffer[i+9];
      
      long delta_m1 = 0;
      long delta_m2 = 0;
      
      long abs_z = z;
      
      
      boolean m1_dir = 0; 
      boolean m2_dir = 0;
      long m1_steps = 0;
      long m2_steps = 0;
      
      forwardKinematics(x, y, &m1_dir, &m2_dir, &m1_steps, &m2_steps);
      
      if(xy_abs_flag){
        delta_m1 = m1_steps-sim_m1;
        delta_m2 = m2_steps-sim_m2;
        sim_m1 = m1_steps;
        sim_m2 = m2_steps;
      } else {
        delta_m1 = m1_steps;
        delta_m2 = m2_steps;
        sim_m1 += m1_dir ? -m1_steps:m1_steps;
        sim_m2 += m2_dir ? -m2_steps:m2_steps;
      }
      
      if(!z_abs_flag){
       sim_f += z;
      }else{
       sim_f = z; 
      }
      
      if(delta_m1<0){
        delta_m1 = abs(delta_m1);
        m1_dir = !m1_dir;
      }
      
      if(delta_m2<0){
        delta_m2 = abs(delta_m2);
        m2_dir = !m2_dir;
      }
      
      command c1 = {
        delta_m1,
        delta_m2,
        m1_dir,
        m2_dir,
        min_step_time,
        min_step_time,
        sim_f
      };
      
      command_list[sim_command_index] = c1;
      sim_command_index++;
      
      if(sim_command_index == MAX_COMMANDS){
        i = buffer_pos;
      }
    }
  }
  
  length_command = sim_command_index;
  current_command_index=-1;
        
}

