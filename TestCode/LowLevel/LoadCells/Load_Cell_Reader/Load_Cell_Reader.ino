#include "HX711.h"

#define cal1 10590//8800
#define cal2 10590
#define cal3 10590//12010

#define DOUT1 5
#define CLK1 4
#define DOUT2 3
#define CLK2 2
#define DOUT3 6
#define CLK3 7

float load1;
float load2;
float load3;
float total;

HX711 scale1(DOUT1, CLK1);
HX711 scale2(DOUT2, CLK2);
HX711 scale3(DOUT3, CLK3);

void setup() {
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
  Serial.println();

  
}
