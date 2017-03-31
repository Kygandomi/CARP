
#include "HX711.h"

#define cal1 -96890
#define cal2 -98980
#define cal3 -93040

#define DOUT1 5
#define CLK1 4
#define DOUT2 3
#define CLK2 2
#define DOUT3 6
#define CLK3 7
#define OUTPIN0 13
#define OUTPIN1 12
#define OUTPIN2 11
#define OUTPIN3 10
#define MAX 1 //in lbs


float load1;
float load2;
float load3;
float total;
int out;
int out0;
int out1;
int out2;
int out3;

HX711 scale1(DOUT1, CLK1);
HX711 scale2(DOUT2, CLK2);
HX711 scale3(DOUT3, CLK3);

void setup() {
  pinMode(OUTPIN0, OUTPUT);
  pinMode(OUTPIN1, OUTPUT);
  pinMode(OUTPIN2, OUTPUT);
  pinMode(OUTPIN3, OUTPUT);
  
  Serial.begin(9600);
  scale1.set_scale(cal1);
  scale1.tare();
  Serial.println("Scale 1 Tared");
  scale2.set_scale(cal2);
  scale2.tare();
  Serial.println("Scale 2 Tared");
  scale3.set_scale(cal3);
  scale3.tare();
  Serial.println("Scale 3 Tared");

}

void loop() {
  load1 = scale1.get_units();
  load2 = scale2.get_units();
  load3 = scale3.get_units();
  total = load1 + load2 + load3;
  
  Serial.print("Load1: ");
  Serial.print(load1, 2);
  Serial.print(" lbs");
  Serial.println();
  
  Serial.print("Load2: ");
  Serial.print(load2, 2);
  Serial.print(" lbs");
  Serial.println();

  Serial.print("Load3: ");
  Serial.print(load3, 2);
  Serial.print(" lbs");
  Serial.println();

  Serial.print("Total: ");
  Serial.print(total, 2);
  Serial.print(" lbs");
  Serial.println();


  if(total > MAX){
    total = MAX;
  }
  out = total/MAX*15;
  
  Serial.print("out: ");
  Serial.print(out);
  Serial.println();

  out0 = 0;
  out1 = 0;
  out2 = 0;
  out3 = 0;
  
  if(out>=8){
    out -= 8;
    out3 = 1;    
  }
  if(out>=4){
    out -= 4;
    out2 = 1;
  }
  if(out>=2){
    out -= 2;
    out1 = 1;
  }
  if(out>=1){
    out-= 1;
    out0 = 1;
  }

  Serial.print("THE OUTS: ");
  Serial.print(out3);
  Serial.print(out2);
  Serial.print(out1);
  Serial.print(out0);
  Serial.println();
  Serial.println();

  digitalWrite(OUTPIN3, out3);
  digitalWrite(OUTPIN2, out2);
  digitalWrite(OUTPIN1, out1);
  digitalWrite(OUTPIN0, out0);

}
