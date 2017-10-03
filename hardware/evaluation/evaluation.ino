 // Accelerometers -----------------------------------------
 struct accelerometer {
  
  int xpin;
  int ypin;
  int zpin;
  
  };
  
 const int x1 = A0;                  
 const int y1 = A1;                  
 const int z1 = A2;                  

 const int x2 = A3;                  
 const int y2 = A4;                  
 const int z2 = A5;                  

 const int x3 = A6;                  
 const int y3 = A7;                  
 const int z3 = A8;                  

 const int x4 = A9;                  
 const int y4 = A10;                  
 const int z4 = A11;                  

double x_value[4];
double y_value[4];
double z_value[4];

double x_gbench[4];
double y_gbench[4];
double z_gbench[4];

/*
 * Array Positions Indicators --------------------------------------------------------------------
 * 0 = arm_left
 * 1 = arm_right
 * 2 = leg_left
 * 3 = leg_right
 */
struct accelerometer accel[4];

//Current Sensor-------------------------------------------
const int current_measure_pin = A12;
const int RS = 10;
const int VOLTAGE_REF = 5;

float sensorValue ;
float current = 0.0;

//Voltage Sensor-------------------------------------------
#define NUM_SAMPLES 10

int sum = 0;                    // sum of samples taken
unsigned char sample_count = 0; // current sample number
float voltage = 0.0;            // calculated voltage

//Function Header Declaration------------------------------
void updateAccel(void);
void updateCurrent(void);
void updateVoltage(void);
void initializeAccel(void);
void updateBatch(void);
void printBatch(void);

void initializeGB(){

    
   //update x_value array
  for (int i = 0; i < 4; i++){
    x_gbench[i] = analogRead(accel[i].xpin);  
  }

  //update y_value array
  for (int i = 0; i < 4; i++){
    y_gbench[i] = analogRead(accel[i].ypin);  
  }

  //update z_value array
  for (int i = 0; i < 4; i++){
    z_gbench[i] = analogRead(accel[i].zpin);  
  }
  
  
  }

void initializeAccel(){

  accel[0].xpin = x1;
  accel[0].ypin = y1;
  accel[0].zpin = z1;
  
  accel[1].xpin = x2;
  accel[1].ypin = y2;
  accel[1].zpin = z2;

  accel[2].xpin = x3;
  accel[2].ypin = y3;
  accel[2].zpin = z3;

  accel[3].xpin = x4;
  accel[3].ypin = y4;
  accel[3].zpin = z4;
  
  }

void updateAccel(){
  
   //update x_value array
  for (int i = 0; i < 4; i++){
    x_value[i] = analogRead(accel[i].xpin);
    delay(5);  
  }

  //update y_value array
  for (int i = 0; i < 4; i++){
    y_value[i] = analogRead(accel[i].ypin);  
    delay(5);
  }

  //update z_value array
  for (int i = 0; i < 4; i++){
    z_value[i] = analogRead(accel[i].zpin);  
    delay(5);
  }
  
  }

void updateCurrent(){

  sensorValue = analogRead(current_measure_pin);
  
  // Remap the ADC value into a voltage number (5V reference)
  sensorValue = (sensorValue * VOLTAGE_REF) / 1023;

  // Follow the equation given by the INA169 datasheet to
  // determine the current flowing through RS. Assume RL = 10k
  // Is = (Vout x 1k) / (RS x RL)
  current = sensorValue / (10 * RS);
  
  }

void updateVoltage(){
  
  // take a number of analog samples and add them up
    while (sample_count < NUM_SAMPLES) {
        sum += analogRead(A2);
        sample_count++;
        delay(10);
    }
    // calculate the voltage
    // use 5.0 for a 5.0V ADC reference voltage
    // 5.015V is the calibrated reference voltage

    voltage = ((float)sum / (float)NUM_SAMPLES * 5.015) / 1024.0;
    
    // voltage multiplied by 11 when using voltage divider that
    // divides by 11. 11.132 is the calibrated voltage divide
    // value

    voltage = voltage * 11.132;
    
    sample_count = 0;
    sum = 0;
    
  }

void updateBatch(){

  updateAccel();
  
  updateCurrent();

  updateVoltage();
  
  }

/*
 * Printing Format
 * eg. 
 * Accel *****
 * arm_left    |arm_right   |leg_left    |leg_right   |      
 * x = 255.00; |x = 255.00; |x = 255.00; |x = 255.00; |
 * y = 255.00; |y = 255.00; |y = 255.00; |y = 255.00; |
 * z = 255.00; |z = 255.00; |z = 255.00; |z = 255.00; |
 * 
 * Current = 2.00
 * Voltage = 6V
 */
void printBatch(){
  
  Serial.println("Accel *****");

  //Print header label as first row
  Serial.print("arm_left    |");
  Serial.print("arm_right   |");
  Serial.print("leg_left    |");
  Serial.print("leg_right   |");
  Serial.println();
  
  //Print x-values of accelerometer as second row
  for (int i = 0; i < 4; i++){
    Serial.print("x = ");
    Serial.print(x_value[i]);
    Serial.print("; |");
  }
  Serial.println();
  //Print y-values of accelerometer as third row
  for (int i = 0; i < 4; i++){
    Serial.print("y = ");
    Serial.print(y_value[i]);
    Serial.print("; |");
  }
Serial.println();
  //Print z-values of accelerometer as fourth row
  for (int i = 0; i < 4; i++){
    Serial.print("z = ");
    Serial.print(z_value[i]);
    Serial.print("; |");
  }
  Serial.println();
  Serial.println();
  Serial.print("Current = ");
  Serial.println(current);

  Serial.print("Voltage = ");
  Serial.println(voltage);
  
  }

void generateData(){

    for (int i = 0; i < 4; i++){
//    Serial.print("x");
//    Serial.print(i + 1);
//    Serial.print(" = ");
    Serial.print(x_value[i]);
    Serial.print(" ");
//    Serial.print("y");
//    Serial.print(i + 1);
//    Serial.print(" = ");
    Serial.print(y_value[i]);
    Serial.print(" ");
//    Serial.print("z");
//    Serial.print(i + 1);
//    Serial.print(" = ");
    Serial.print(z_value[i]);
    Serial.print(" ");
    
  }
    
  }

void setup() {
  // initialize the serial communications:
  Serial.begin(9600);
  
  // initialize accelerometers pins
  initializeAccel();

  // initialize gravitational biase array
  initializeGB();
  
}

void loop() {
  
  updateBatch();

//  printBatch();
  
  generateData();
  
  Serial.println();
  
  delay(100);
}
