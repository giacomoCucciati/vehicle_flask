//https://lastminuteengineers.com/l293d-motor-driver-shield-arduino-tutorial/

#include <AFMotor.h>
#include <Servo.h> 

#define temperaturePin A0
#define luminosityPin A1
int incomingByte = 0; // for incoming serial data
char inData[20];
int index = 0;
int myspeed = 0;
AF_DCMotor motor(1);


Servo myservo;  // create servo object to control a servo
int pos = 90;  // variable to store the servo position

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  myservo.attach(10);   
}

// the loop routine runs over and over again forever:
void loop() {
  index = 0;
  while (true) {
    if (Serial.available() > 0) {
      // read the incoming byte:
      incomingByte = Serial.read();
      if ((char)incomingByte == '\n') {
        Serial.println("End of message");
        break;
      }
      inData[index] = incomingByte;
      index = index + 1;
      if (index == 19) {
        break;
      }
      // say what you got:
      Serial.print("I received: ");
      Serial.println(incomingByte, DEC);
    }
  }
  inData[index] = 0;
  
  String str((char*)inData);
  Serial.println(str);

  if (str.equals("a")) {
    pos = 170;
    myservo.write(pos);
    myservo.write(pos-2);
  } else if (str.equals("d")) {
    pos = 0;
    myservo.write(pos);
    myservo.write(pos+2);
  } else if (str.equals("-a") || str.equals("-d")) {
    pos = 90;
    myservo.write(pos);
  } else if (str.equals("s")) {
    motor.run(FORWARD);
    motor.setSpeed(150);
  } else if (str.equals("w")) {
    motor.run(BACKWARD);
    motor.setSpeed(150);
  } else if (str.equals("-w") || str.equals("-s")) {
    motor.setSpeed(0);
    motor.run(RELEASE);
  }

  // Now turn off motor
  //motor.run(RELEASE);
  Serial.print("pos: ");
  Serial.println(pos);  
  Serial.print("vel: ");
  Serial.println(myspeed);
}
