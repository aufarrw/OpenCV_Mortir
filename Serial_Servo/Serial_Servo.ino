#include <Servo.h>

Servo elevasi;
double resultDouble;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  elevasi.attach(5);
  elevasi.write(0);
  Serial.println(elevasi.read());
}

void loop() {
  // put your main code here, to run repeatedly:
  while(Serial.available()==0){} //wait until there is input 
  String result = Serial.readString();
  resultDouble = result.toDouble();
  Serial.println(result);
  elevasi.write(resultDouble);
  Serial.println(elevasi.read());
}
