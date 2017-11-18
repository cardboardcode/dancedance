#include <Arduino.h>
#include <Timer.h>
#include <avr/io.h>

//Sensor data
unsigned char x1=0, y1=0, z1=0;
unsigned char x2=0, y2=0, z2=0;
unsigned char x3=0, y3=0, z3=0;
unsigned char x4=0, y4=0, z4=0;
unsigned char cur=0, vol=0;

//Data set
const int frameLength = 16;
typedef struct data{
	unsigned char frameID;
	unsigned char voltage;
	unsigned char current;
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

TConfigFrame cfgFrame;

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

const int pin_vol = A12;
const int pin_cur = A13;

//flow control
const int bufferSize = 32;
unsigned char sendID = 0;         //head
unsigned char slotID = 0;         //tail
unsigned char ackID = 0;          //last ack ID: next id to receive

unsigned char ackByte;            //ack or nack
unsigned char frameID;            //ack or nack frameID

unsigned char frameBuffer[bufferSize][frameLength];

void sampleReading();
void sendMessage();
void receiveFeedback();
void startSend();
void startRecv();

int8_t sendEvent;

Timer t;
unsigned long samplePeriod = 4;
unsigned long sendPeriod = 4;
unsigned long recvPeriod = 4;
unsigned long fastSendPeriod = 3;

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

	t.every(samplePeriod, sampleReading);
	t.task(2, startSend, 1);
	t.task(3, startRecv, 1);
}

void loop()
{
	t.update();
}

void startSend() {
	sendEvent = t.every(sendPeriod, sendMessage);
}

void startRecv() {
	t.every(recvPeriod, receiveFeedback);
}

void sampleReading() {
	//Serialize the data into a frame (char array)
	cfgFrame.frameID = slotID;
	cfgFrame.voltage = analogRead(pin_vol);
	cfgFrame.current = analogRead(pin_cur);
	cfgFrame.sensor1X = analogRead(pin_x1) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor1Y = analogRead(pin_y1) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor1Z = analogRead(pin_z1) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor2X = analogRead(pin_x2) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor2Y = analogRead(pin_y2) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor2Z = analogRead(pin_z2) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor3X = analogRead(pin_x3) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor3Y = analogRead(pin_y3) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor3Z = analogRead(pin_z3) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor4X = analogRead(pin_x4) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor4Y = analogRead(pin_y4) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.sensor4Z = analogRead(pin_z4) >> 2;                  //Keep the data range to fit in 1 byte
	cfgFrame.checkSum = (slotID ^ cfgFrame.voltage ^ cfgFrame.current ^ cfgFrame.sensor1X ^ cfgFrame.sensor1Y ^ cfgFrame.sensor1Z ^ cfgFrame.sensor2X ^ cfgFrame.sensor2Y
			 ^ cfgFrame.sensor2Z ^ cfgFrame.sensor3X ^ cfgFrame.sensor3Y ^ cfgFrame.sensor3Z ^ cfgFrame.sensor4X ^ cfgFrame.sensor4Y ^ cfgFrame.sensor4Z);

	if(ackID == (slotID + 1) % bufferSize)   {                            //no more empty space, speed up send
		Serial.print("V");
		t.stop(sendEvent);
		sendEvent = t.every(fastSendPeriod, sendMessage);
	}else {
		slotID = (slotID + 1) % bufferSize;
	}
	memcpy(frameBuffer[cfgFrame.frameID], &cfgFrame, frameLength);
}

void sendMessage() {
	if(sendID != slotID) {                                //some frame in the buffer
		Serial3.write(frameBuffer[sendID], frameLength);
		sendID = (sendID + 1) % bufferSize;
	}
}

void receiveFeedback(){
	if(Serial3.available()==2) {
		ackByte = Serial3.read();
		frameID = Serial3.read();         //next frame to be received
//		Serial.write(ackByte);
//		Serial.println(frameID);
		if(ackByte == 'A') {
			ackID = frameID;          //all previous frames received
		} else if (ackByte == 'N'){
			ackID = frameID;                                 //all previous frames received
			sendID = frameID;                                //resent the frame
		}
	}
}
