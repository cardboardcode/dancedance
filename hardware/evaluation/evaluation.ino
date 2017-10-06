/*
ADXL335 Accelerometer Demo
Derek Chafin
September 22, 2011
Public Domain

Demonstrates how to use the ADXL335 library

Pin Connections:

analog 0: connected to x-axis
analog 1: connected to y-axis
analog 2: connected to z-axis
aref: connected to +3.3V
*/

#include <ADXL335.h>

const int pin_x0 = A0;
const int pin_y0 = A1;
const int pin_z0 = A2;

const int pin_x1 = A3;
const int pin_y1 = A4;
const int pin_z1 = A5;

const int pin_x2 = A6;
const int pin_y2 = A7;
const int pin_z2 = A8;

const int pin_x3 = A9;
const int pin_y3 = A10;
const int pin_z3 = A11;

const float aref = 3.3;

ADXL335 accel0(pin_x0, pin_y0, pin_z0, aref);
ADXL335 accel1(pin_x1, pin_y1, pin_z1, aref);
ADXL335 accel2(pin_x2, pin_y2, pin_z2, aref);
ADXL335 accel3(pin_x3, pin_y3, pin_z3, aref);


void setup()
{
  Serial.begin(9600);
  
  Serial.println("X0,\tY0,\tZ0,\tX1,\tY1,\tZ1,X2,\tY2,\tZ2,X3,\tY3,\tZ3,");
}

void loop()
{
  //this is required to update the values
  accel0.update();
  accel1.update();
  accel2.update();
  accel3.update();
  
  //this tells us how long the string is
  int string_width;

  float x0;
  float y0;
  float z0;
  
  float x1;
  float y1;
  float z1;

  float x2;
  float y2;
  float z2;
  
  float x3;
  float y3;
  float z3;
  
  //for these variables see wikipedia's
  //definition of spherical coordinates
  float rho;
  float phi;
  float theta;  

//  accel0.setThreshold(0.3);
  
  x0 = accel0.getX();
  y0 = accel0.getY();
  //if the project is laying flat and top up the z axis reads ~1G
  z0 = accel0.getZ();

  x1 = accel1.getX();
  y1 = accel1.getY();
  //if the project is laying flat and top up the z axis reads ~1G
  z1 = accel1.getZ();

  x2 = accel2.getX();
  y2 = accel2.getY();
  //if the project is laying flat and top up the z axis reads ~1G
  z2 = accel2.getZ();

  x3 = accel3.getX();
  y3 = accel3.getY();
  //if the project is laying flat and top up the z axis reads ~1G
  z3 = accel3.getZ();
  
//  rho = accel0.getRho();
//  phi = accel0.getPhi();
//  theta = accel0.getTheta();

  Serial.print(formatFloat(x0, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(y0, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(z0, 2, &string_width));
  Serial.print(",\t");

  Serial.print(formatFloat(x1, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(y1, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(z1, 2, &string_width));
  Serial.print(",\t");

  Serial.print(formatFloat(x2, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(y2, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(z2, 2, &string_width));
  Serial.print(",\t");

  Serial.print(formatFloat(x3, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(y3, 2, &string_width));
  Serial.print(",\t");
  Serial.print(formatFloat(z3, 2, &string_width));
  Serial.print(",\t");
  Serial.println("");
  
//  Serial.print(formatFloat(rho, 2, &string_width));
//  Serial.print(",\t");
//  Serial.print(formatFloat(phi, 2, &string_width));
//  Serial.print(",\t");
//  Serial.print(formatFloat(theta, 2, &string_width));
//  Serial.println("");
  
  delay(100);
}

//this function was taken from my format float library
String formatFloat(double value, int places, int* string_width)
{
  //if value is positive infinity
  if (isinf(value) > 0)
  {
    return "+Inf";
  }
    
  //Arduino does not seem to have negative infinity
  //keeping this code block for reference
  //if value is negative infinity
  if(isinf(value) < 0)
  {
    return "-Inf";
  }
  
  //if value is not a number
  if(isnan(value) > 0)
  {
    return "NaN";
  }
  
  //always include a space for the dot
  int num_width = 1;

  //if the number of decimal places is less than 1
  if (places < 1)
  {
    //set places to 1
    places = 1;
    
    //and truncate the value
    value = (float)((int)value);
  }
  
  //add the places to the right of the decimal
  num_width += places;
  
  //if the value does not contain an integral part  
  if (value < 1.0 && value > -1.0)
  {
    //add one for the integral zero
    num_width++;
  }
  else
  {

    //get the integral part and
    //get the number of places to the left of decimal
    num_width += ((int)log10(abs(value))) + 1;
  }
  //if the value in less than 0
  if (value < 0.0)
  {
    //add a space for the minus sign
    num_width++;
  }
  
  //make a string the size of the number
  //plus 1 for string terminator
  char s[num_width + 1]; 
  
  //put the string terminator at the end
  s[num_width] = '\0';
  
  
  //initalize the array to all zeros
  for (int i = 0; i < num_width; i++)
  {
    s[i] = '0';
  }
  
  //characters that are not changed by 
  //the function below will be zeros
  
  //set the out variable string width
  //lets the caller know what we came up with
  *string_width = num_width;
  
  //use the avr-libc function dtosrtf to format the value
  return String(dtostrf(value,num_width,places,s));  
}
