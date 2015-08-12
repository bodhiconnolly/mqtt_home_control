#include <SPI.h>         
#include <Ethernet.h>
#include "PubSubClient.h"


char clientID[] = "roomPIR";
char onTopic[] = "system/pir/room";
char outTopic[] = "room/pir/status";
char updateTopic[] = "room/pir/keepalive";
char updateMessage[] = "still alive";


//the amount of milliseconds the sensor has to be low 
//before we assume all motion has stopped
long unsigned int waitTime = 300000;  //sending the same message twice in ms 
long unsigned int inactiveTime = 300000;  //time before room is inactive in ms (300000)
long unsigned int lastActiveTime = 0;
long unsigned int lastSendTime = 0;
long unsigned int lastUpdateTime = 0;
int updateTime = 15000; //send keep active message in ms

int pirPin = 3;    //the digital pin connected to the PIR sensor's output
int ledPin = 13;
int calibrationTime = 10;
int pir_active;
int prevState = 0;


//network information
byte server[] = { 10, 1, 1, 100 };
int port = 1882;
byte mac[] = { 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xFF };
byte ip[] = { 10, 1, 1, 150 };


// Callback function header
void callback(char* topic, byte* payload, unsigned int length);

EthernetClient ethClient;
PubSubClient client(server, port, callback, ethClient);

void setup() {
	Serial.begin(9600);
	Ethernet.begin(mac, ip);
	if (client.connect(clientID)) {
		client.publish(onTopic, "ON");
	}
	pinMode(pirPin, INPUT);
	pinMode(ledPin, OUTPUT);
	//digitalWrite(pirPin, LOW);

	//give the sensor some time to calibrate
	Serial.print("calibrating sensor ");
	for (int i = 0; i < calibrationTime; i++){
		Serial.print(".");
		delay(1000);
	}
	Serial.println(" done");
	Serial.println("SENSOR ACTIVE");
	delay(50);
}

void sendStatus(int status){
	
	if (status==1){
		client.publish(outTopic, "active");
		Serial.println("sent active");
	}
	else{
		client.publish(outTopic, "inactive");
		Serial.println("sent inactive");

	}
	delay(50);
}

void callback(char* topic, byte* payload, unsigned int length) {

}


void loop(){

	pir_active = !(digitalRead(pirPin));
	Serial.print(pir_active);
	Serial.print(" was ");
	Serial.println(prevState);
	//if (pir_active == !0){
	//	if (pir_active==1){
	//		Serial.println("active");
	//	}
	//}
	if (pir_active != prevState){		//state has changed
		if (pir_active==1){
			Serial.println("gone high");
			sendStatus(1);
			digitalWrite(ledPin, HIGH);
			lastActiveTime = millis();
			lastSendTime = millis();
			prevState = 1;
		}
		else{
			if (millis() > (lastActiveTime + inactiveTime)){
				Serial.println("gone low");
				sendStatus(0);
				digitalWrite(ledPin, LOW);
				lastSendTime = millis();
				prevState = 0;
			}
		}
	}
	else if (pir_active==prevState){     //state hasn't changed
		if (pir_active==1){
			Serial.println("still high");
			lastActiveTime = millis();
		}
		else if (pir_active==0){
			Serial.println("still low");
			if (millis() > lastSendTime + waitTime){
				sendStatus(0);
				digitalWrite(ledPin, LOW);
				lastSendTime = millis();
			}
		}
	}
	if (millis() > lastUpdateTime + updateTime){
		client.publish(updateTopic, updateMessage);
		lastUpdateTime = millis();
	}
	delay(50);
}

