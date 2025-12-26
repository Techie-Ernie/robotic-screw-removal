
// Bottle test

const int StepX = 2;
const int DirX = 5;
const int StepY = 3;
const int DirY = 6;


void setup() {
  pinMode(StepX,OUTPUT);
  pinMode(DirX,OUTPUT);
  //pinMode(StepY,OUTPUT);
  //pinMode(DirY,OUTPUT);
  Serial.begin(9600);


}

void loop() {
    digitalWrite(DirX, HIGH); // set direction, HIGH for clockwise, LOW for anticlockwise
    digitalWrite(DirY, HIGH);
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');
        Serial.print("You sent me: ");
        Serial.println(data);
        if (data == "bottle")
        {
            for(int x = 0; x<200; x++) { // loop for 200 steps
                digitalWrite(StepX,HIGH);
                delayMicroseconds(500);
                digitalWrite(StepX,LOW); 
                delayMicroseconds(500);
            }
            delay(1000); 
        }

    }

}
