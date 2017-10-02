
// these constants describe the pins. They won't change:
const int xpin = A0;                  // x-axis of the accelerometer
const int ypin = A1;                  // y-axis
const int zpin = A2;                  // z-axis (only on 3-axis models)

struct accelero{

  int x;
  int y;
  int z;
  
  };

double value_window_x[10];
double value_window_y[10];
double value_window_z[10];

double average_window_x[10];
double average_window_y[10];
double average_window_z[10];

struct accelero a1;

float average_x;
float average_y;
float average_z;

float super_average_x;
float super_average_y;
float super_average_z;

float idle_current_x = 0.0;
float idle_prev_x = 0.0;
float idle_current_y = 0.0;
float idle_prev_y = 0.0;
float idle_current_z = 0.0;
float idle_prev_z = 0.0;

void initAccel(void);
void initWindow(void);
void updateWindow(void);
void updateAverage(void);
void getAverage(void);

void initAccel(){
  a1.x = xpin;
  a1.y = ypin;
  a1.z = zpin;
  
  }


void initWindow(){

  for (int i = 0; i < 10; i++){
    
    value_window_x[i] = analogRead(a1.x);
    value_window_y[i] = analogRead(a1.y);
    value_window_z[i] = analogRead(a1.z);
    
  }
  
}

void updateWindow(){

   //Push all values toward the left to make space for the new value
   for (int i = 1; i < 10 ;i++){

      value_window_x[i-1] = value_window_x[i];
      value_window_y[i-1] = value_window_y[i];
      value_window_z[i-1] = value_window_z[i];
    
   }

  //Insert new value at the end of the value_window

  double diff_x = analogRead(a1.x) - value_window_x[9];
  double diff_y = analogRead(a1.y) - value_window_y[9];
  double diff_z = analogRead(a1.z) - value_window_z[9];
  if (diff_x > 5 || diff_x < -5){
  value_window_x[9] = analogRead(a1.x);
  }
  if (diff_y > 5 || diff_y < -5){
  value_window_y[9] = analogRead(a1.y);
  }
  if (diff_z > 5 || diff_z < -5){
  value_window_z[9] = analogRead(a1.z);
  }
  
  delay(20);
  
}

void setup() {
  // initialize the serial communications:
  Serial.begin(9600);

  initAccel();

  initWindow();
  
}

void getAverage(){

  double local_x;
  double local_y;
  double local_z;
  
  for (int i = 0; i < 10; i++){
    local_x += value_window_x[i];
    local_y += value_window_y[i];
    local_z += value_window_z[i];   
  }

  average_x = local_x/10;
  average_y = local_y/10;
  average_z = local_z/10;
  
}


double getSuperAverage(){

  double local_x;
  double local_y;
  double local_z;
  
  for (int i = 0; i < 10; i++){
    local_x += average_window_x[i];
    local_y += average_window_y[i];
    local_z += average_window_z[i];   
  }

  super_average_x = local_x/10;
  super_average_y = local_y/10;
  super_average_z = local_z/10;

}


void updateAverage(){

   //Push all values toward the left to make space for the new value
   for (int i = 1; i < 10 ;i++){

      average_window_x[i-1] = average_window_x[i];
      average_window_y[i-1] = average_window_y[i];
      average_window_z[i-1] = average_window_z[i];
    
   }
     
   average_window_x[9] = average_x;
   average_window_y[9] = average_y;
   average_window_z[9] = average_z; 
}

boolean isIdle(){

    int compare_x = average_window_x[0];
    int compare_y = average_window_y[0];
    int compare_z = average_window_z[0];
    
    for (int i = 1; i < 10; i++){
      if (average_window_x[i] != compare_x){
          return false;
        }
      if (average_window_y[i] != compare_y){
          return false;
        }
      if (average_window_z[i] != compare_z){
          return false;
        }
      }
    return true;
    
}

boolean isStationary(){

     if (idle_current_x - idle_prev_x > 2)
        return false;
     if (idle_current_y - idle_prev_y > 2)
        return false;
     if (idle_current_y - idle_prev_y > 2)
        return false;

     if (idle_current_x - idle_prev_x < -2)
        return false;
     if (idle_current_y - idle_prev_y < -2)
        return false;
     if (idle_current_z - idle_prev_z < -2)
        return false;  

      return true;
  }

void loop() {
  
  updateWindow();

  getAverage();

  updateAverage();
  
  getSuperAverage();
  
  if(isIdle){
    idle_current_x = super_average_x;
    idle_current_y = super_average_y;
    idle_current_z = super_average_z;
    }
  
  if (idle_current_x - idle_prev_x > 2)
      Serial.println("RIGHT ------------------------->");
  else if (idle_current_x - idle_prev_x <M -2)
      Serial.println("LEFT-------------------------<");

  if (idle_current_y - idle_prev_y > 2)
      Serial.println("DOWN ------------------------->");
  else if (idle_current_y - idle_prev_y < -2)
      Serial.println("UP-------------------------<");

  if (idle_current_z - idle_prev_z > 2)
      Serial.println("FRONT ------------------------->");
  else if (idle_current_z - idle_prev_z < -2)
      Serial.println("BACK-------------------------<");


//   if (isStationary)
//      Serial.println("NOT MOVING");
  
  idle_prev_x = idle_current_x;
  idle_prev_y = idle_current_y;
  idle_prev_z = idle_current_z;
  
  delay(50);
}
