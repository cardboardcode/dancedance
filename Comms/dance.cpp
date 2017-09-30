#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <avr/io.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>

#define MAX_PACKET_SIZE 64

//Semaphore for barrier implementation
SemaphoreHandle_t xSemaphoreCount = NULL;
SemaphoreHandle_t xSemaphore1 = NULL;
SemaphoreHandle_t xSemaphore2 = NULL;
SemaphoreHandle_t xSemaphore3 = NULL;
SemaphoreHandle_t xSemaphore4 = NULL;

int totalThreads = 4;
int threadCount = 0;
int count=0;

//Sensor data
int x1=0, y1=0, z1=0;
int x2=0, y2=0, z2=0;
int x3=0, y3=0, z3=0;
int x4=0, y4=0, z4=0;

//Data set
const int frameLength = 28;
typedef struct data{
	int frameID;
	int sensor1X;
	int sensor1Y;
	int sensor1Z;
	int sensor2X;
	int sensor2Y;
	int sensor2Z;
	int sensor3X;
	int sensor3Y;
	int sensor3Z;
	int sensor4X;
	int sensor4Y;
	int sensor4Z;
	int checkSum;
} TConfigFrame;


TConfigFrame cfgFrame;
TConfigFrame returnFrame;

//Sliding window flow control
int bufferSize = 8;
int currentID = 0;
int ackID = 8;
unsigned char* frameBuffer[8];

void readSensor1(void *pvParameters);
void readSensor2(void *pvParameters);
void readSensor3(void *pvParameters);
void readSensor4(void *pvParameters);
void serializeMessage(void *pvParameters);
void receiveFeedback(void *pvParameters);

void setup() {
	Serial.begin(115200);
	Serial3.begin(115200);
	xSemaphoreCount = xSemaphoreCreateMutex();
	xSemaphore1 = xSemaphoreCreateBinary();
	xSemaphore2 = xSemaphoreCreateBinary();
	xSemaphore3 = xSemaphoreCreateBinary();
	xSemaphore4 = xSemaphoreCreateBinary();
	xSemaphoreGive(xSemaphoreCount);
	xSemaphoreGive(xSemaphore1);
	xSemaphoreGive(xSemaphore2);
	xSemaphoreGive(xSemaphore3);
	xSemaphoreGive(xSemaphore4);

	xTaskCreate(readSensor1, "readSensor1", 100, NULL, 4, NULL);
	xTaskCreate(readSensor2, "readSensor2", 100, NULL, 4, NULL);
	xTaskCreate(readSensor3, "readSensor3", 100, NULL, 4, NULL);
	xTaskCreate(readSensor4, "readSensor4", 100, NULL, 4, NULL);
	xTaskCreate(serializeMessage, "serializeMessage", 100, NULL, 3, NULL);
	xTaskCreate(receiveFeedback, "receiveFeedback", 100, NULL, 3, NULL);
}

void loop()
{
  // Empty. Things are done in Tasks.
}

void readSensor1(void *p) {
	TickType_t pxPreviousWakeTime1 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore1, 0) == pdTRUE) {
			//x1 = analogRead(A0);
			//y1 = analogRead(A1);
			//z1 = analogRead(A2);
			x1 = x1+0;
			y1 = y1+1;
			z1 = z1+2;
			if(xSemaphoreTake(xSemaphoreCount, 5) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime1, 150);
	}
}

void readSensor2(void *p) {
	TickType_t pxPreviousWakeTime2 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore2, 0) == pdTRUE) {
	//      x2 = analogRead(A3);
	//      y2 = analogRead(A4);
	//      z2 = analogRead(A5);
			x2 = x2 + 3;
			y2 = y2 + 4;
			z2 = z2 + 5;
			if(xSemaphoreTake(xSemaphoreCount, 5) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime2,  150);
	}
}

void readSensor3(void *p) {
	TickType_t pxPreviousWakeTime3 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore3, 0) == pdTRUE) {
	//      x3 = analogRead(A6);
	//      y3 = analogRead(A7);
	//      z3 = analogRead(A8);
			x3 = x3 + 6;
			y3 = y3 + 7;
			z3 = z3 + 8;
			if(xSemaphoreTake(xSemaphoreCount, 5) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
    	vTaskDelayUntil(&pxPreviousWakeTime3, 150);
	}
}

void readSensor4(void *p) {
	TickType_t pxPreviousWakeTime4 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphore4, 0) == pdTRUE) {
	//      x4 = analogRead(A9);
	//      y4 = analogRead(A10);
	//      z4 = analogRead(A11);
			x4 = x4 + 9;
			y4 = y4 + 10;
			z4 = z4 + 11;
			if(xSemaphoreTake(xSemaphoreCount, 5) == pdTRUE) {
				threadCount = threadCount + 1;
				xSemaphoreGive(xSemaphoreCount);
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime4, 150);
	}
}

void loadToBuffer() {
	//Serialize the data into a frame (char array)
	cfgFrame.frameID = currentID + '0';
	cfgFrame.sensor1X = x1 + '0';
	cfgFrame.sensor1Y = y1 + '0';
	cfgFrame.sensor1Z = z1 + '0';
	cfgFrame.sensor2X = x2 + '0';
	cfgFrame.sensor2Y = y2 + '0';
	cfgFrame.sensor2Z = z2 + '0';
	cfgFrame.sensor3X = x3 + '0';
	cfgFrame.sensor3Y = y3 + '0';
	cfgFrame.sensor3Z = z3 + '0';
	cfgFrame.sensor4X = x4 + '0';
	cfgFrame.sensor4Y = y4 + '0';
	cfgFrame.sensor4Z = z4 + '0';
	cfgFrame.checkSum = (currentID ^ x1 ^ y1 ^ z1 ^ x2 ^ y2 ^ z2 ^ x3 ^ y3 ^ z3 ^ x4 ^ y4 ^ z4) + '0';
	currentID = (currentID + 1) % bufferSize;
	unsigned char message[frameLength];
	memcpy(message, &cfgFrame, frameLength);
//	frameBuffer[currentID] = message;
	Serial3.write(message, frameLength);
	Serial3.write('\r');
}

void serializeMessage(void *p) {
	TickType_t pxPreviousWakeTime5 = xTaskGetTickCount();
	while(1) {
		//all tasks complete
		if(threadCount == totalThreads) {
			if(xSemaphoreTake(xSemaphoreCount, 5) == pdTRUE) {
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
		vTaskDelayUntil(&pxPreviousWakeTime5, 150);
	}
}

void receiveFeedback(void *p){
	TickType_t pxPreviousWakeTime6 = xTaskGetTickCount();
	while(1) {
		if(Serial3.available()) {
			Serial.write(Serial3.read());
		}
		vTaskDelayUntil(&pxPreviousWakeTime6, 50);
	}
}
