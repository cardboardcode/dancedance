/*
  ADXL3xx

  Reads an Analog Devices ADXL3xx accelerometer and communicates the
  acceleration to the computer. The pins used are designed to be easily
  compatible with the breakout boards from SparkFun, available from:
  http://www.sparkfun.com/commerce/categories.php?c=80

  The circuit:
  - analog 0: accelerometer self test
  - analog 1: z-axis
  - analog 2: y-axis
  - analog 3: x-axis
  - analog 4: ground
  - analog 5: vcc

  created 2 Jul 2008
  by David A. Mellis
  modified 30 Aug 2011
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/ADXL3xx
*/

// these constants describe the pins. They won't change:
const int groundpin = 18;             // analog input pin 4 -- ground
const int powerpin = 19;              // analog input pin 5 -- voltage
const int xpin = A3;                  // x-axis of the accelerometer
const int ypin = A2;                  // y-axis
const int zpin = A1;                  // z-axis (only on 3-axis models)

int xdef;
int ydef;
int zdef;

int gbench = 0;

int xworld = 0;

int xprev;
int diff;
int diff2;

int counter = 0;

int idlevalue;

void setup() {
  // initialize the serial communications:
  Serial.begin(9600);

  // Provide ground and power by using the analog inputs as normal digital pins.
  // This makes it possible to directly connect the breakout board to the
  // Arduino. If you use the normal 5V and GND pins on the Arduino,
  // you can remove these lines.
  pinMode(groundpin, OUTPUT);
  pinMode(powerpin, OUTPUT);
  digitalWrite(groundpin, LOW);
  digitalWrite(powerpin, HIGH);

  analogRead(ypin);

  gbench = analogRead(ypin);
  
}

void loop() {
  
  xdef = analogRead(ypin);

  xdef -= gbench;
  
  diff = xdef - xprev;
  
  if (diff >= 5 || diff <= -5){
    
    xworld += diff;
  }
  else{

    if (idlevalue != xworld ){
        diff2 = idlevalue - xworld;


    if (diff2 < 0){
        Serial.println("Moving in Negative");
      }
    else if (diff2 > 0){
        Serial.println("Moving in Positive");
      }
      
      }
    
    idlevalue = xworld;
    }
  // print a tab between values:
//  Serial.print("\t");
//  Serial.print(analogRead(ypin));
//  // print a tab between values:
//  Serial.print("\t");
//  Serial.print(analogRead(zpin));
  xprev = xdef;

//  Serial.print("y in world coordinate = ");
  Serial.println();
  
  // delay before next reading:
  delay(50);
}
