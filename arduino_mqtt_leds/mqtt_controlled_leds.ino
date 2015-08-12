#include <SPI.h>         
#include <Ethernet.h>
#include "PubSubClient.h"

#define RED 7
#define GREEN 9 
#define BLUE 3

char clientID[] = "roomLEDtest";
char onTopic[] = "system/leds/room";
char inTopic[] = "room/lights/strips/#";
String reply[30];

//network information
byte server[] = { 192, 168, 1, 100 };
int port = 1882;
byte mac[] = { 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xCC };
byte ip[] = { 192, 168, 1, 77 };


// Callback function header
void callback(char* topic, byte* payload, unsigned int length);

EthernetClient ethClient;
PubSubClient client(server, port, callback, ethClient);

void parse(String message, String topic){
	String channel = topic.substring(topic.length() - 1, topic.length());
	int outPort;
		Serial.print(channel);
		Serial.println(message);
		if (channel == "r"){
			outPort = RED;
		}
		else if (channel == "g"){
			outPort = GREEN;
		}
		else if (channel == "b"){
			outPort = BLUE;
		}
		int messageValue = constrain((message).toInt(), 0, 255);
		analogWrite(outPort, messageValue);
		//Serial.println(outPort);
		//Serial.println(messageValue);
			
		//reply = "print this";
		//char replyArray[200];
		//reply.toCharArray(replyArray, 200);
		//return replyArray
	
}

void setup() {
	Serial.begin(9600);
	Ethernet.begin(mac, ip);
	Serial.println("here");

	if (client.connect(clientID)) {
		client.publish("led/info", "ON");
		client.subscribe(inTopic);
		Serial.println("connected and subscribed");
	}
	Serial.println("and here");

}

void callback(char* topic, byte* payload, unsigned int length) {
	payload[length] = '\0';
	String strPayload = String((char*)payload);
	//Serial.println(strPayload);
	parse(strPayload, String(topic));
	//Serial.println(reply);
	//client.publish(replytopic, reply);
}

void loop() {
	client.loop();
}




