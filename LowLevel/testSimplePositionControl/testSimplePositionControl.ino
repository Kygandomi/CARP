// Painting Robot MQP 
// Low Level Code V1

#define BAUD           115200
#define MAX_BUF        64  

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

int m1_dir = 1;
int m1_steps = 0;
int m1_step_time = 500;
unsigned long m1_start_time = 0;

int m2_dir = 1;
int m2_steps = 0;
int m2_step_time = 500;
unsigned long m2_start_time = 0;

void setup_motors() {
    // Set up Pin Modes
    pinMode(M1_ENB,OUTPUT);
    pinMode(M1_DIR,OUTPUT);
    pinMode(M1_PUL,OUTPUT);

    pinMode(M2_ENB,OUTPUT);
    pinMode(M2_DIR,OUTPUT);
    pinMode(M2_PUL,OUTPUT);

    // Set up Enables
    digitalWrite(M1_ENB,LOW);
    digitalWrite(M2_ENB,LOW);
    
    digitalWrite(M1_DIR,LOW);
    digitalWrite(M2_DIR,HIGH);
}

void setup(){
  // Open Serial Port
  Serial.begin(BAUD);
  
  // Set up Motors
  setup_motors();
}

void loop(){
        if(m1_steps == 0 && m2_steps == 0 && !Serial.available()){
            Serial.println("?");
//            Serial.write(0xFE);
//            Serial.write(0x00);
//            Serial.write(0xEF);
        }
  
	if(m1_steps == 0 && m2_steps == 0 && Serial.available()){
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
			processBuffer();
                        buffer_pos = 0;
		}
	}

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
}

void processBuffer(){
	// Read and Interpret from Buffer
	m1_dir = buffer[1];
	m1_steps = (buffer[2] << 8) + buffer[3];
        m1_step_time = (buffer[4] << 8) + buffer[5];

        m2_dir = buffer[6];
	m2_steps = (buffer[7] << 8) + buffer[8];
	m2_step_time = (buffer[9] << 8) + buffer[10];

        // Set M1 Direction
        if(m1_dir > 0){
          PORTD |= _BV(PD7);
        } else {
          PORTD &= ~_BV(PD7);
        }
        
        // Set M2 Direction
        if(m2_dir > 0){
          PORTG |= _BV(PG2);
        } else {
          PORTG &= ~_BV(PG2);
        }

        // Print for Debugging
        Serial.println("Data:");
        Serial.println(m1_dir);
        Serial.println(m1_steps);
        Serial.println(m1_step_time);
        Serial.println(m2_dir);
        Serial.println(m2_steps);
        Serial.println(m2_step_time);
}

