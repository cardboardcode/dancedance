#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <avr/io.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>

#define MAX_PACKET_SIZE 64
#define samplePeriod pdMS_TO_TICKS(150UL)
#define commPeriod pdMS_TO_TICKS(100UL)
#define waitTime pdMS_TO_TICKS(2UL)

//Semaphore for barrier implementation
SemaphoreHandle_t xSemaphore1 = NULL;
SemaphoreHandle_t xSemaphore2 = NULL;
SemaphoreHandle_t xSemaphore3 = NULL;
SemaphoreHandle_t xSemaphore4 = NULL;

int totalThreads = 4;
int threadCount = 0;

SemaphoreHandle_t xSemaphoreBuffer = NULL;
SemaphoreHandle_t xSemaphoreCount = NULL;
SemaphoreHandle_t xSemaphoreTail = NULL;
SemaphoreHandle_t xSemaphoreHead = NULL;

//Sensor data
unsigned char x1=0, y1=0, z1=0;
unsigned char x2=0, y2=0, z2=0;
unsigned char x3=0, y3=0, z3=0;
unsigned char x4=0, y4=0, z4=0;

//Data set
const int frameLength = 14;
typedef struct data{
	unsigned char frameID;
	unsigned char sensor1X;
	unsigned char sensor1Y;
	unsigned char sensor1Z;
	unsigned char sensor2X;
	unsigned char sensor2Y;
	unsigned char sensor2Z;
	unsigned char sensor3X;
	unsigned char sensor3Y;
	unsigned char sensor3Z;
	unsigned char sensor4X;
	unsigned char sensor4Y;
	unsigned char sensor4Z;
	unsigned char checkSum;
} TConfigFrame;

// Accelerometers Configurations
const int pin_x1 = A0;
const int pin_y1 = A1;
const int pin_z1 = A2;

const int pin_x2 = A3;
const int pin_y2 = A4;
const int pin_z2 = A5;

const int pin_x3 = A6;
const int pin_y3 = A7;
const int pin_z3 = A8;

const int pin_x4 = A9;
const int pin_y4 = A10;
const int pin_z4 = A11;

//flow control
const int bufferSize = 16;
int sendID = 0;         //head
int slotID = 0;         //tail
int ackID = 0;          //last ack ID: next id to receive

unsigned char frameBuffer[bufferSize][frameLength];

void readSensor1(void *pvParameters);
void readSensor2(void *pvParameters);
void readSensor3(void *pvParameters);
void readSensor4(void *pvParameters);
void serializeMessage(void *pvParameters);
void sendMessage(void *pvParameters);
void receiveFeedback(void *pvParameters);

void setup() {
	Serial.begin(115200);
	Serial3.begin(115200);

	//Handshaking, wait until raspberry pi say 'H', then reply 'A' to start the transmission
	while(!Serial3.available() || Serial3.read() != 'H') {
		//Serial.println("Check Rx");
		delay(100);
	}
	Serial3.write('A');
	while(!Serial3.available() || Serial3.read() != 'A') {
		//Serial.println("Check Tx");
		delay(100);
	}
	Serial.println("Connected");

	xSemaphoreCount = xSemaphoreCreateMutex();
	xSemaphoreBuffer = xSemaphoreCreateMutex();
	xSemaphore1 = xSemaphoreCreateBinary();
	xSemaphore2 = xSemaphoreCreateBinary();
	xSemaphore3 = xSemaphoreCreateBinary();
	xSemaphore4 = xSemaphoreCreateBinary();
	xSemaphoreGive(xSemaphoreCount);
	xSemaphoreGive(xSemaphoreBuffer);
	xSemaphoreGive(xSemaphore1);
	xSemaphoreGive(xSemaphore2);
	xSemaphoreGive(xSemaphore3);
	xSemaphoreGive(xSemaphore4);

	xTaskCreate(readSensor1, "readSensor1", 100, NULL, 3, NULL);
	xTaskCreate(readSensor2, "readSensor2", 100, NULL, 3, NULL);
	xTaskCreate(readSensor3, "readSensor3", 100, NULL, 3, NULL);
	xTaskCreate(readSensor4, "readSensor4", 100, NULL, 3, NULL);
	xTaskCreate(serializeMessage, "serializeMessage", 100, NULL, 2, NULL);
	xTaskCreate(sendMessage, "sendMessage", 100, NULL, 1, NULL);
	xTaskCreate(receiveFeedback, "receiveFeedback", 100, NULL, 1, NULL);
}

void loop()
{
  // Empty. Things are done in Tasks.
}

void readSensor1(void *p) {
	TickType_t pxPreviousWakeTime1 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore1, 0) == pdTRUE) {
	      	x1 = analogRead(pin_x1) >> 2;
	      	y1 = analogRead(pin_y1) >> 2;
	      	z1 = analogRead(pin_z1) >> 2;
			if(xSemaphoreTake(xSemaphoreCount, waitTime) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime1, samplePeriod);
	}
}

void readSensor2(void *p) {
	TickType_t pxPreviousWakeTime2 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore2, 0) == pdTRUE) {
      		x2 = analogRead(pin_x2) >> 2;
      		y2 = analogRead(pin_y2) >> 2;
      		z2 = analogRead(pin_z2) >> 2;
			if(xSemaphoreTake(xSemaphoreCount, waitTime) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime2,  samplePeriod);
	}
}

void readSensor3(void *p) {
	TickType_t pxPreviousWakeTime3 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore3, 0) == pdTRUE) {
      		x3 = analogRead(pin_x3) >> 2;
      		y3 = analogRead(pin_y3) >> 2;
      		z3 = analogRead(pin_z3) >> 2;
      		if(xSemaphoreTake(xSemaphoreCount, waitTime) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
    	vTaskDelayUntil(&pxPreviousWakeTime3, samplePeriod);
	}
}

void readSensor4(void *p) {
	TickType_t pxPreviousWakeTime4 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore4, 0) == pdTRUE) {
			x4 = analogRead(pin_x4) >> 2;
			y4 = analogRead(pin_y4) >> 2;
			z4 = analogRead(pin_z4) >> 2;
			if(xSemaphoreTake(xSemaphoreCount, waitTime) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime4, samplePeriod);
	}
}

void loadToBuffer() {
	//Serialize the data into a frame (char array)
	TConfigFrame cfgFrame;
	cfgFrame.frameID = slotID;
	cfgFrame.sensor1X = x1;
	cfgFrame.sensor1Y = y1;
	cfgFrame.sensor1Z = z1;
	cfgFrame.sensor2X = x2;
	cfgFrame.sensor2Y = y2;
	cfgFrame.sensor2Z = z2;
	cfgFrame.sensor3X = x3;
	cfgFrame.sensor3Y = y3;
	cfgFrame.sensor3Z = z3;
	cfgFrame.sensor4X = x4;
	cfgFrame.sensor4Y = y4;
	cfgFrame.sensor4Z = z4;
	cfgFrame.checkSum = (slotID ^ x1 ^ y1 ^ z1 ^ x2 ^ y2 ^ z2 ^ x3 ^ y3 ^ z3 ^ x4 ^ y4 ^ z4);
//	Serial.print(emptyID);
//	Serial.print(",");
//	Serial.print(x1);
//	Serial.print(",");
//	Serial.print(y1);
//	Serial.print(",");
//	Serial.print(z1);
//	Serial.print(",");
//	Serial.print(x2);
//	Serial.print(",");
//	Serial.print(y2);
//	Serial.print(",");
//	Serial.print(z2);
//	Serial.print(",");
//	Serial.print(x3);
//	Serial.print(",");
//	Serial.print(y3);
//	Serial.print(",");
//	Serial.print(z3);
//	Serial.print(",");
//	Serial.print(x4);
//	Serial.print(",");
//	Serial.print(y4);
//	Serial.print(",");
//	Serial.println(z4);

	if(xSemaphoreTake(xSemaphoreBuffer, 2) == pdTRUE) {
		if(ackID == (slotID + 1) % bufferSize)                              //no more empty space, signal overflow
			Serial.println("V");
		else {
			slotID = (slotID + 1) % bufferSize;
		}
		xSemaphoreGive(xSemaphoreBuffer);
		memcpy(frameBuffer[cfgFrame.frameID], &cfgFrame, frameLength);
	}
}

void serializeMessage(void *p) {
	TickType_t pxPreviousWakeTime5 = xTaskGetTickCount();
	while(1) {
		//all tasks complete
		if(threadCount == totalThreads) {
			if(xSemaphoreTake(xSemaphoreCount, waitTime) == pdTRUE) {
				threadCount = 0;
				xSemaphoreGive(xSemaphoreCount);
			}
			loadToBuffer();

			//release the binary semaphore for the CPU to take next set of reading
			xSemaphoreGive(xSemaphore1);
			xSemaphoreGive(xSemaphore2);
			xSemaphoreGive(xSemaphore3);
			xSemaphoreGive(xSemaphore4);
		}
		vTaskDelayUntil(&pxPreviousWakeTime5, samplePeriod);
	}
}

void sendMessage(void *p) {
	unsigned char id;
	TickType_t pxPreviousWakeTime6 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphoreBuffer, waitTime) == pdTRUE) {
			if(sendID != slotID) {                                //some frame in the buffer
				id = sendID;
				sendID = (sendID + 1) % bufferSize;
				xSemaphoreGive(xSemaphoreBuffer);
				Serial3.write(frameBuffer[id], frameLength);
			} else {
				xSemaphoreGive(xSemaphoreBuffer);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime6, commPeriod);
	}
}

void receiveFeedback(void *p){
	char ackByte;
	int frameID;
	TickType_t pxPreviousWakeTime7 = xTaskGetTickCount();
	while(1) {
		if(Serial3.available()==2) {
			ackByte = Serial3.read();
			frameID = Serial3.read();         //next frame to be received
			//Serial.write(ackByte);
			//Serial.println(frameID);
			if(ackByte == 'A') {
				if(xSemaphoreTake(xSemaphoreBuffer, waitTime) == pdTRUE) {
					ackID = frameID;          //all previous frames received
					xSemaphoreGive(xSemaphoreBuffer);
				}
			} else if (ackByte == 'N'){
				if(xSemaphoreTake(xSemaphoreBuffer, waitTime) == pdTRUE) {
					ackID = frameID;                                 //all previous frames received
					sendID = frameID;                                //resent the frame
					xSemaphoreGive(xSemaphoreBuffer);
				}
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime7, commPeriod);
	}
}

