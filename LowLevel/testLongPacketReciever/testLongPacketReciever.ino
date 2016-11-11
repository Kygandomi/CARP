// Painting Robot MQP 
// Low Level Code V1
#include <PID_v1.h>

#define BAUD           115200
#define MAX_BUF        15  
#define MAX_COMMANDS   400

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

// Command Structure
struct command_t{
  int m1_steps;
  int m2_steps;
  
  boolean m1_dir;
  boolean m2_dir;
  
  unsigned int m1_step_time;
  unsigned int m2_step_time;
    
  int firgelli_pos;
} ;

// For Command Buffer
int current_command_index = -1;
int length_command = 0;
command_t command_list[MAX_COMMANDS];

// Global Variables
int buffer[MAX_BUF];
int buffer_pos;
bool startbit = false;

// Motor Step Definitions and Start Times
long m1_steps = 0;
int m1_step_time = 0;
boolean m1_pulse = false;
unsigned long m1_start_time = 0;

long m2_steps = 0;
int m2_step_time = 0;
boolean m2_pulse = false;
unsigned long m2_start_time = 0;

// Firgelli Controller Variables
double Setpoint, Input, Output;

// Current position of gantry in M1/M2 space
long current_m1 = 0;
long current_m2 = 0;
long current_f = 0;

// Simulated Index
int sim_command_index = 0;
long sim_m1 = 0;
long sim_m2 = 0;
long sim_f = 0;

//Define the aggressive and conservative Tuning Parameters
double aggKp=1, aggKi=0, aggKd=0;
double consKp=1, consKi=0.05, consKd=0.25;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);

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
  
  // Initial Firgelli Setpoint
  Setpoint = 700;
  
  // Turn on PID
  myPID.SetMode(AUTOMATIC);
  delay(1);
}


void loop(){
//  Serial.print("current_m1 : ");
//  Serial.print(current_m1);
//  Serial.print(" current_m2 : ");
//  Serial.println(current_m2);
  
  if(current_command_index < 0 && sim_command_index == 0 && !Serial.available()){
    Serial.write(0xFE);
    Serial.write(0x00);
    Serial.write(0xEF);
  }
	else if(current_command_index < 0 && Serial.available()){
		int c = Serial.read();

		if(c == int(0xFE)){
		  startbit = true;
		}
		if(startbit){
			if(buffer_pos < MAX_BUF) buffer[buffer_pos++]=c;
      
        else if(buffer_pos == MAX_BUF && c != int(0xEF)){
	    buffer_pos = 0;
	    startbit = false;
        } 
		}
		if(startbit && c == int(0xEF)){
  		startbit = false;
  		processBuffer();
      buffer_pos = 0;
		}
	} 
  //move to position
  else if(current_command_index>=0){
    if(run()){
      startCommand();
    }
  }
  
  runFirgelli();
}

void forwardKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local){
	
  float mag = sqrt(pow(delta_x, 2) + pow(delta_y, 2));
	float angle = atan2(delta_y, delta_x); 

	float s1 = mag*sin(angle - 0.785398);
	float s2 = mag*cos(angle - 0.785398);

//	if(s1 < 0)
//	  *m1_dir = true;
//	else
//  	*m1_dir = false;
//	if(s2 < 0)
//	  *m2_dir = true;
//	else
//	  *m2_dir = false;

	*m1_steps_local = (long)s1;
	*m2_steps_local = (long)s2;
}

void startCommand(){
  current_command_index++;
  if(current_command_index>=length_command){
    current_command_index = -1;
    return;
  }
  command_t current_command = command_list[current_command_index];
  
  m1_steps = current_command.m1_steps;
  m2_steps = current_command.m2_steps;
          
  m1_step_time = current_command.m1_step_time;
  m2_step_time = current_command.m2_step_time;
  
  boolean m1_dir = current_command.m1_dir;
  boolean m2_dir = current_command.m2_dir;
  
  Setpoint = current_command.firgelli_pos;
  
  if(m1_dir){
    current_m1 -= current_command.m1_steps;
  }else{
    current_m1 += current_command.m1_steps;
  }
  if(m2_dir){
    current_m2 -= current_command.m2_steps;
  }else{
    current_m2 += current_command.m2_steps;
  }
  
  // Set M1 Direction
  if(m1_dir){
    PORTD |= _BV(PD7);
  } else {
    PORTD &= ~_BV(PD7);
  }
          
  // Set M2 Direction
  if(m2_dir){
    PORTG |= _BV(PG2);
   } else {
    PORTG &= ~_BV(PG2);
   }
}

boolean run(){
//  Serial.print("Vars: ");
//  Serial.print(current_command_index);
//  Serial.print(" of ");
//  Serial.print(length_command);
//  Serial.print(" | ");
//  Serial.print(m1_steps);
//  Serial.print(" ");
//  Serial.print(m2_steps);
//  Serial.print(" | ");
//  Serial.print(m1_step_time);
//  Serial.print(" ");
//  Serial.print(m2_step_time);
//  Serial.println(" ");
  
  if(m1_steps == 0 && m2_steps == 0){
    if(m1_pulse){
      PORTC &= ~_BV(PC3);
      m1_pulse=false;
    }
    if(m2_pulse){
      PORTC &= ~_BV(PC2);
      m2_pulse=false;
    }
    return true;
  } 
   
  else {     
    if(m1_steps != 0){
      if(m1_pulse){
        PORTC &= ~_BV(PC3);
        m1_pulse=false;
      }
      else if(micros() - m1_start_time > (m1_step_time - 20) ){
        PORTC |= _BV(PC3);
        m1_steps--;
        m1_start_time = micros();
        m1_pulse=true;
      }
    }
    
    if(m2_steps != 0){
      if(m2_pulse){
        PORTC &= ~_BV(PC2);
        m2_pulse=false;
      }
      else if(micros() - m2_start_time > (m2_step_time - 20)){
        PORTC |= _BV(PC2);
        m2_steps--;
        m2_start_time = micros();
        m2_pulse=true;
      }
    }
    
    return false;   
   }
}

void runFirgelli(){
  // Figure out where to go and how to move
  Input = analogRead(POT);
  current_f = Input;
      
  double gap = abs(Setpoint-Input); //distance away from setpoint
  if(gap<10)
  {  
    //we're close to setpoint, use conservative tuning parameters
    myPID.SetTunings(consKp, consKi, consKd);
  }
  else
  {
    //we're far from setpoint, use aggressive tuning parameters
    myPID.SetTunings(aggKp, aggKi, aggKd);
  }
      
  // Compute PID
  myPID.Compute();
  
  // Set Direction of Firgelli
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
  if(buffer_pos == 3){
    //   Serial.print("Current buffer value is :");
    //   Serial.println(buffer[buffer_pos-1]);
    if(buffer[buffer_pos-2] == int(0xEE)){
      length_command = sim_command_index;
      current_command_index = -1;
      sim_command_index = 0;
      startCommand();
    } 
  } else {
    
    //Serial.println("Processing the buffer!");

    if(sim_command_index >= MAX_COMMANDS){
      return;
    }
    
    if(sim_command_index == 0){
      sim_m1 = current_m1;
      sim_m2 = current_m2;
      sim_f = current_f; 
    }

    int i=1;
    if(i+SERIAL_ELEMENT_LEN < buffer_pos){
      int x = (buffer[i] << 8) + buffer[i+1];
      int y = (buffer[i+2] << 8) + buffer[i+3];
      boolean xy_abs_flag = (boolean)buffer[i+4];
      
      int z = (buffer[i+5] << 8) + buffer[i+6];
      boolean z_abs_flag = (boolean)buffer[i+7];
      
      int min_step_time = (buffer[i+8] << 8) + buffer[i+9];
      
      int delta_m1 = 0;
      int delta_m2 = 0;
      
      boolean m1_dir = false; 
      boolean m2_dir = false;
      long m1_steps_local = 0;
      long m2_steps_local = 0;
      
//      Serial.print(x);
//      Serial.print(",");
//      Serial.print(y);
//      Serial.print(" | ");
//      Serial.println(xy_abs_flag);
      forwardKinematics(x, y, &m1_steps_local, &m2_steps_local);
      
      if(xy_abs_flag){
        delta_m1 = m1_steps_local-sim_m1;
        delta_m2 = m2_steps_local-sim_m2;
        sim_m1 = m1_steps_local;
        sim_m2 = m2_steps_local;
      } else {
        delta_m1 = m1_steps_local;
        delta_m2 = m2_steps_local;
        sim_m1 += delta_m1;
        sim_m2 += delta_m2;
      }
      
      if(!z_abs_flag){
       sim_f += z;
      }else{
       sim_f = z; 
      }
      
//      Serial.print(delta_m1);
//      Serial.print(",");
//      Serial.print(delta_m2);
//      Serial.print(" | ");
//      Serial.print(sim_m1);
//      Serial.print(",");
//      Serial.println(sim_m2);
//      Serial.println("-----------------");
      
      m1_dir = false ;
      m2_dir = false ;

      if(delta_m1 < 0){
        delta_m1 = abs(delta_m1);
        m1_dir = true;
      }
      if(delta_m2 < 0){
        delta_m2 = abs(delta_m2);
        m2_dir = true;
      }

      int m1_step_time_local=min_step_time;
      int m2_step_time_local=min_step_time;

      //Make the motion linear by reducing speed of the shorter path
      if((delta_m1>delta_m2) && (delta_m2>0)){
        m2_step_time_local = (int)(((float)delta_m1/(float)delta_m2)*min_step_time);
      }
      else if((delta_m2>delta_m1) && (delta_m1>0)){
        m1_step_time_local = (int)(((float)delta_m2/(float)delta_m1)*min_step_time);
      }
      
      command_t c1 = {
        delta_m1,
        delta_m2,
        m1_dir,
        m2_dir,
        m1_step_time_local,
        m2_step_time_local,
        sim_f
      };
      
      command_list[sim_command_index] = c1;
      sim_command_index++;
    }
  }
}

