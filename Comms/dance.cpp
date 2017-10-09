#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <avr/io.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>

#define MAX_PACKET_SIZE 64

//Semaphore for barrier implementation
SemaphoreHandle_t xSemaphoreCount = NULL;
SemaphoreHandle_t xSemaphoreEmptyID = NULL;
SemaphoreHandle_t xSemaphoreSendID = NULL;
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
const int bufferSize = 8;
int emptySlots = 8;
int itemSlots = 0;
int emptyID = 0;
int sendID = 0;
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
		Serial.println("Wait for Pi");
	}
	Serial.println("Connected");
	Serial3.write('A');

	xSemaphoreCount = xSemaphoreCreateMutex();
	xSemaphoreEmptyID = xSemaphoreCreateMutex();
	xSemaphoreSendID = xSemaphoreCreateMutex();
	xSemaphore1 = xSemaphoreCreateBinary();
	xSemaphore2 = xSemaphoreCreateBinary();
	xSemaphore3 = xSemaphoreCreateBinary();
	xSemaphore4 = xSemaphoreCreateBinary();
	xSemaphoreGive(xSemaphoreCount);
	xSemaphoreGive(xSemaphoreEmptyID);
	xSemaphoreGive(xSemaphoreSendID);
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
	cfgFrame.frameID = emptyID;
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
	cfgFrame.checkSum = (emptyID ^ x1 ^ y1 ^ z1 ^ x2 ^ y2 ^ z2 ^ x3 ^ y3 ^ z3 ^ x4 ^ y4 ^ z4);
//	unsigned char message[frameLength];
//	frameBuffer[emptyID] = message;
//	Serial3.write(frameBuffer[emptyID], frameLength);
//	emptyID = (emptyID + 1) % bufferSize;
	if(xSemaphoreTake(xSemaphoreEmptyID, 5) == pdTRUE) {
		if(emptySlots < 1) {                              //no more empty space, signal overflow
			Serial.println("V");
		} else {
//			frameBuffer[emptyID] = message;
//			Serial3.write(frameBuffer[sendID], frameLength);
			memcpy(frameBuffer[emptyID], &cfgFrame, frameLength);
			emptyID = (emptyID + 1) % bufferSize;
//			sendID = (sendID + 1) % bufferSize;
			emptySlots = emptySlots - 1;
			if(xSemaphoreTake(xSemaphoreSendID, 5) == pdTRUE) {
				 itemSlots = itemSlots + 1;
				 xSemaphoreGive(xSemaphoreSendID);
			}
		}
		xSemaphoreGive(xSemaphoreEmptyID);
	}
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

void sendMessage(void *p) {
	int id = 0;
	boolean send = false;
	TickType_t pxPreviousWakeTime6 = xTaskGetTickCount();
	while(1) {
		if(xSemaphoreTake(xSemaphoreSendID, 5) == pdTRUE) {
			if(itemSlots > 0) {                             //contains data to send
				id = sendID;
				send = true;
//				Serial3.write(frameBuffer[sendID], frameLength);
				sendID = (sendID + 1) % bufferSize;
				itemSlots = itemSlots - 1;
			} else {
				send = false;
			}
			xSemaphoreGive(xSemaphoreSendID);
		}
		if (send) {
			Serial3.write(frameBuffer[id], frameLength);
		}
		vTaskDelayUntil(&pxPreviousWakeTime6, 100);
	}
}

void receiveFeedback(void *p){
	char ackByte;
	int frameID;
	TickType_t pxPreviousWakeTime7 = xTaskGetTickCount();
	while(1) {
		if(Serial3.available()==2) {
			ackByte = Serial3.read();
			frameID = Serial3.read();
			Serial.write(ackByte);
			Serial.print(frameID);
			if(ackByte == 'A') {
				if(xSemaphoreTake(xSemaphoreEmptyID, 5) == pdTRUE) {
					emptySlots = (8-emptyID + frameID) % 8 + 1;      //update empty space
					xSemaphoreGive(xSemaphoreEmptyID);
				}
			} else if (ackByte == 'N'){
				if(xSemaphoreTake(xSemaphoreSendID, 5) == pdTRUE) {
					sendID = frameID;                                //resent the frame
					xSemaphoreGive(xSemaphoreSendID);
				}
			}
		}
		vTaskDelayUntil(&pxPreviousWakeTime7, 100);
	}
}
