#include <Servo.h>

Servo myServo;      
const int servoPin = 12;   

void setup() {
  // initialize serial if desired
  Serial.begin(115200);
  Serial.println("Servo test start");
  
  myServo.attach(servoPin);   
}

void loop() {
  myServo.write(167);
  delay(670);  
  myServo.write(0);
  delay(670);
  
  
}


// n20: d10; y+