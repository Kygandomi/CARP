// Painting Robot MQP 
// Long Packet Reciever Low Level Code
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

// Structure Created for Storing Individual Robot Movement Routines
struct command_t{
  int m1_steps;
  int m2_steps;
  
  boolean m1_dir;
  boolean m2_dir;
  
  unsigned int m1_step_time;
  unsigned int m2_step_time;
    
  int firgelli_pos;
};

// Command Buffer used for keeping a list of Movement Commands
int current_command_index = -1;
int length_command = 0;
command_t command_list[MAX_COMMANDS];

// Serial Buffer used for keeping a list of bytes read over Serial
int buffer[MAX_BUF];
int buffer_pos = 0;
int startbit_pos = 0;
boolean startbit = false;

// Motor Definitions used to send pulses to stepper motors
long m1_steps = 0;
unsigned int m1_step_time = 0;
boolean m1_pulse = false;
unsigned long m1_start_time = 0;

long m2_steps = 0;
unsigned int m2_step_time = 0;
boolean m2_pulse = false;
unsigned long m2_start_time = 0;

// Current position of gantry in M1/M2 space
long current_m1 = 0;
long current_m2 = 0;
long current_f = 0;

// Simulated Index for initializing commands
int sim_command_index = 0;
long sim_m1 = 0;
long sim_m2 = 0;
long sim_f = 0;

// Firgelli PID Controller Variables
double Setpoint, Input, Output;

//Tuning Parameters for Firgelli PID
double aggKp=1, aggKi=0, aggKd=0;
double consKp=1, consKi=0.05, consKd=0.25;

//Firgelli PID from Arduino PID Library
PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);

// Method used for motor initialization
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

// Setup used for initialization of low level code
void setup(){
  // Open Serial Port
  Serial.begin(BAUD);
  
  // Set up Motors
  setup_motors();
  
  // Set PID output limits 
  myPID.SetOutputLimits(-255,255);
  
  // Initial Firgelli Setpoint
  Setpoint = 500;
  
  // Turn on PID
  myPID.SetMode(AUTOMATIC);
  delay(1);
}

// Loop where code is ran repeatedly !
void loop(){

  // If there are no commands left in the list and we're not reading over Serial    
  if(current_command_index < 0 && sim_command_index == 0 && !Serial.available()){
      // Report our status back to the High Level
      Serial.write(0xFE);
      Serial.write(0x00);
      Serial.write(0xEF);
      delay(5);
  }

  // Else if there are no commands left in the list and there is something to read over Serial
  else if(current_command_index < 0 && Serial.available()){
    // Read the character from the Serial Buffer 
    int c = Serial.read();

    // If the character is the start byte
    if(c == int(0xFE) && !startbit){
      // Set the start bit flag to true
      startbit = true;
      startbit_pos = buffer_pos;
      
      // Add Start byte to buffer
      if(buffer_pos < MAX_BUF) buffer[buffer_pos++]=c;
    }

    // If the start character has been found
    else if(startbit){
      
      // Given that buffer pos is valid, add element to buffer
      if(buffer_pos < MAX_BUF) buffer[buffer_pos++]=c;

      // Else if buffer pos is too big
      else if(buffer_pos == MAX_BUF){
         // Then reset the message as we've overflown
         buffer_pos = 0;
         startbit = false;
      }
          
      if(buffer_pos > SERIAL_ELEMENT_LEN + startbit_pos){
         startbit = false;
         processBuffer();
         buffer_pos = 0; 
      }
    }
  } 

  //Else there are commands to be run
  else if(current_command_index>=0){
    // Run the commands
    if(run()){
      // When Run has completed call startCommand
      startCommand();
    }
  }
  
  // Continously run Firgelli PID
  runFirgelli();
}


// This method is called before a motor movement command is called
void startCommand(){
  
  Serial.print("Command ");
  Serial.print(current_command_index);
  Serial.print(" of ");
  Serial.println(length_command);
  
  // Increment the Current Command Index
  current_command_index++;
  
  // If the current command index exceeds the total length of commands
  if(current_command_index>=length_command){
    // reset current command index for next time
    current_command_index = -1;
    return;
  }
  
  // Get the Current Command
  command_t current_command = command_list[current_command_index];
  
  // Get Motor Steps, Directions, and Step Times
  m1_steps = current_command.m1_steps;
  m2_steps = current_command.m2_steps;
  
  m1_step_time = current_command.m1_step_time;
  m2_step_time = current_command.m2_step_time;
  
  boolean m1_dir = current_command.m1_dir;
  boolean m2_dir = current_command.m2_dir;
  
  // Set the Firgelli set point
  Setpoint = current_command.firgelli_pos;
  Serial.println(Setpoint);
  
  // Configure the current position of the robot in M1/M2 space
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

// This method pulses the stepper motor
boolean run(){
  // If there are no steps to run
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
   
  // Given that there are steps to run
  else {   
    // Given that motor 1 has steps to execute  
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
    
    // Given that motor 2 has steps to execute
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

// This method is for running the Firgelli PID
void runFirgelli(){
  // Figure out where to go and how to move
  Input = analogRead(POT);
  current_f = Input;
  
  // Determine distance away from setpoint    
  double gap = abs(Setpoint-Input); 
  if(gap<10){  
    //If we're close to setpoint, use conservative tuning parameters
    myPID.SetTunings(consKp, consKi, consKd);
  }
  else{
    //If we're far from setpoint, use aggressive tuning parameters
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

// This method is for performing the Forward Kinematics of the Robot
void forwardKinematics(long delta_x, long delta_y, long* m1_steps_local, long* m2_steps_local){
    float s2 = (delta_x+delta_y)*1.09;//*0.70710678118*1.09;//=//*.7707463915;
    float s1 = (delta_y-delta_x)*1.09;//*0.70710678118*1.09;//=//*.7707463915;

    *m1_steps_local = (long)s1;
    *m2_steps_local = (long)s2;
}

// This method is used to process the Serial Buffer
void processBuffer(){
  Serial.println("Processing Buffer");
  int i = 1;
  if(i + SERIAL_ELEMENT_LEN <= buffer_pos){
      int x = (buffer[i] << 8) + buffer[i+1];
      int y = (buffer[i+2] << 8) + buffer[i+3];
      int z = (buffer[i+4] << 8) + buffer[i+5];
      
      int min_step_time = (buffer[i+6] << 8) + buffer[i+7]; 
      
      boolean xy_abs_flag = (boolean)(buffer[i+8] & 0x02);
      boolean z_abs_flag = (boolean)(buffer[i+8] & 0x04);
      boolean go_flag = (boolean)(buffer[i+8] & 0x01);
      
      int end_bit = buffer[i+9];
   
      Serial.print(x);
      Serial.print(" ");
      Serial.print(y);
      Serial.print(" ");
      Serial.print(z);
      Serial.print(" | ");
      Serial.print(min_step_time);
      Serial.print(" | ");
      Serial.print(xy_abs_flag);
      Serial.print(" ");
      Serial.print(z_abs_flag);
      Serial.print(" ");
      Serial.println(go_flag);   
      
      if(end_bit != 239){
       Serial.println("Something went wrong o_o");
       return; 
      }
      
      // Given that current_command_index is -1
      if(current_command_index == -1){
        if(sim_command_index >= MAX_COMMANDS){
          return;
        }
      
        if(sim_command_index == 0){
          sim_m1 = current_m1;
          sim_m2 = current_m2;
          sim_f = current_f; 
        }
  
        int delta_m1 = 0;
        int delta_m2 = 0;
      
        boolean m1_dir = false; 
        boolean m2_dir = false;
        long m1_steps_local = 0;
        long m2_steps_local = 0;
      
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
         Serial.println("Not Z abs");
         sim_f += z;
        }else{
        Serial.println("Z abs");
         sim_f = z; 
        }
      
        m1_dir = false;
        m2_dir = false;

        if(delta_m1 < 0){
          delta_m1 = abs(delta_m1);
          m1_dir = true;
        }
        
        if(delta_m2 < 0){
          delta_m2 = abs(delta_m2);
          m2_dir = true;
        }

        unsigned int m1_step_time_local=min_step_time;
        unsigned int m2_step_time_local=min_step_time;

        //Make the motion linear by reducing speed of the shorter path
        if((delta_m1>delta_m2) && (delta_m2>0)){
          m2_step_time_local = (unsigned int)min((((float)delta_m1/(float)delta_m2)*min_step_time), 65000);
        }
        else if((delta_m2>delta_m1) && (delta_m1>0)){
          m1_step_time_local = (unsigned int)min((((float)delta_m2/(float)delta_m1)*min_step_time), 65000);
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
        
       // If Go flag execute the list of commands and reset global variables
       if(go_flag > 0){
          Serial.println("Go Go Go!");
          length_command = sim_command_index;
          current_command_index = -1;
          sim_command_index = 0;
          startCommand();
      }
    }
  }
}


