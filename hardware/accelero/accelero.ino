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
const int xpin = A0;                  // x-axis of the accelerometer
const int ypin = A1;                  // y-axis
const int zpin = A2;                  // z-axis (only on 3-axis models)

struct accelero{

  int x;
  int y;
  int z;
  
  };

double value_window[10];
double average_window[10];
struct accelero a1;
float average;
float superaverage;
float idle_current = 0.0;
float idle_prev = 0.0;

void initAccel(void);
void initWindow(void);
void updateWindow(void);
void updateAverage(int);
double getAverage(void);

void initAccel(){
  
  a1.z = zpin;
  
  }


void initWindow(){

  for (int i = 0; i < 10; i++){

    value_window[i] = analogRead(a1.z);
    
  }
  
}

void updateWindow(){

   //Push all values toward the left to make space for the new value
   for (int i = 1; i < 10 ;i++){

      value_window[i-1] = value_window[i];
    
   }

  //Insert new value at the end of the value_window
  
  double diff = analogRead(a1.z) - value_window[9];
  if (diff > 5 || diff < -5){
  value_window[9] = analogRead(a1.z);
  }
  
  delay(20);
  
}

void setup() {
  // initialize the serial communications:
  Serial.begin(9600);

  initAccel();

  initWindow();
  
}

double getAverage(){

  double local;
  
  for (int i = 0; i < 10; i++){
    local += value_window[i];    
  }

  local = local/10;

  return local;
}


double getSuperAverage(){

  double local;
  
  for (int i = 0; i < 10; i++){
    local += average_window[i];    
  }

  local = local/10;

  return local;
}

void printWindow(){
  
  for (int i = 0; i < 10; i++){

    Serial.print(value_window[i]);
    Serial.print(", ");
    
    }
     
}

void updateAverage(int newinput){

   //Push all values toward the left to make space for the new value
   for (int i = 1; i < 10 ;i++){

      average_window[i-1] = average_window[i];
    
   }  
   average_window[9] = newinput;
 
}

boolean isIdle(){

    int compare = average_window[0];
    
    for (int i = 1; i < 10; i++){
      if (average_window[i] != compare){
          return false;
        }
      }
    return true;
}
void loop() {
  
  updateWindow();
  average = getAverage();

  updateAverage(average);
  superaverage = getSuperAverage();
  
  if(isIdle){
    idle_current = superaverage;
    }
  
  if (idle_current - idle_prev > 2)
      Serial.println("FRONT ------------------------->");
  else if (idle_current - idle_prev < -2)
      Serial.println("BACK-------------------------<");
  else 
      Serial.println("NOT MOVING");
  
  idle_prev = idle_current;
  
  delay(50);
}
