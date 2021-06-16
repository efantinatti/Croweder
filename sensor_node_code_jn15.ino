/*Croweder - 
 * Sensor node code to count number of people entering and sending/receiving messages via MQTT
 * June 15, 2021
 */

#include <PubSubClient.h>
#include <WiFiEsp.h>
#include "secrets.h"

/*WiFi and MQTT Parameters*/
/*Edit the secrets.h file with your SSID and PASS*/
//sensitive data is contained in secrets.h
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;
int status=WL_IDLE_STATUS;/*the Wifi radio's status. Used to confirm whether a WiFi adapter is connected.*/


//Setting up WiFi and MQTT Clients
WiFiEspClient client;
PubSubClient mqttClient(client);

//MQTT Parameters Setup
const char mqttServer[] = "sep769.fantinatti.net";
const int mqttPort     = 1883;
const char topic[]  = "SEP769";

const char username[] = "SEP769"; //authentication token here
const char password[] = "123";
const char clientID[] = "amirSEP769";

/* Defines pins for ultrasonic sensors*/
#define echoPin1 2 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPin1 3 //attach pin D3 Arduino to pin Trig of HC-SR04

/*Define PIR pin*/
#define PIRpin 13           //Set the digital 13 to PIR

/* Define LED Pin*/
#define countLED 8           //Set the digital 8 to LED
#define mqttLED 9           //Set the digital 9 to LED

/*Variables being counted*/
int roomcount = 0;
int adults = 0;
int children = 0;

/*This variable is a boolean used on whether to send an mqtt message*/
bool record = 0;

/*These variables are used to find the heigh by finding min distance to sensor*/
int min_distance1 = 2000;
float height;

/*d to floor is the distance to the floor from the sensor
 * trigger is the change in distance required to trigger a measurement
 * tWindow is the window in which a person passes through the door
 * tDelay is the time counter after a recording has started
 * dir is the direction
 * msgPayload is the char array to store MQTT message
  */
int d_to_floor_1;
int trigger = 10;
int uTrig = 0;
int pTrig = 0;
int tWindow = 2000;
long tDelay=0;
char msgPayload[100];
int dir;
int pirStatus=0;
int prev_distance = 0;
int roomlimit = 1;

void setup() {
  //Open serial ports to Serial Monitor and ESP8266
  Serial.begin(115200);
  Serial1.begin(115200);

  //Setup LED
  pinMode(countLED,OUTPUT);     //initialize the  led pin as output 
  pinMode(mqttLED,OUTPUT);     //initialize the  led pin as output 

  //Setup ultrasonic sensor
  pinMode(trigPin1, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin1, INPUT); // Sets the echoPin as an INPUT

  //Setup PIR sensor
  pinMode( PIRpin,INPUT);     //initialize the  PIR pin as input
  
  //Just to see program is running
  digitalWrite(countLED,HIGH);

  //To allow sensors to initialize
  delay(1000);
  
  //Connect to WiFi
  wifiConnect();

  //Attempt to connect to the MQTT broker
  mqttConnect();

  //Calibrate the distance between the sensor and the ground
  d_to_floor_1 = calibrateDistance(echoPin1,trigPin1);

  Serial.print("Calibrated distance 1: ");
  Serial.println(d_to_floor_1);

  delay(1000);
  
}


void loop() {
  // loop to keep mqtt Client Connection
  mqttClient.loop();
    
  //wifiCheck();

  // Measure distance, store previous distance
  // Calculate difference between distance and the calibration distance
  int dist1 = ultraSonic(echoPin1, trigPin1);
  int diff1 = abs(d_to_floor_1-dist1);
  int diff2 = abs(d_to_floor_1-prev_distance);
  prev_distance = dist1;
  
  //Measure PIR pin
  pirStatus = digitalRead(PIRpin);

  //While PIR sensor is triggered but ultrasonic is not, check to see if ultrasonic gets triggered
  //If so this is direction 1 (going inside)
  while (pirStatus && !record){
    pTrig = 1;
    dist1 = ultraSonic(echoPin1, trigPin1);
    diff1 = abs(d_to_floor_1-dist1);
    diff2 = abs(d_to_floor_1-prev_distance);
    Serial.println("Waiting for ultrasonic trigger");
    if(diff1>trigger && diff2 > trigger){
      uTrig = 1;
      record = true;
      dir = 1;
      Serial.println("Ultrasonic sensor triggered");
    }
    tDelay = millis();
    prev_distance = dist1;
    pirStatus = digitalRead(PIRpin);
  }

  //Ultrasonic gets triggered if the difference between the distance to the floor and measured
  //distance is larger than some trigger. 
  //The previous difference also has to be greater than the trigger
  if (diff1 > trigger  && diff2> trigger && !record){
    tDelay=millis();
    record=true;
    min_distance1 = dist1;
    dir = 0;
    uTrig = 1;
  }

  //Record minimum distance (max height) in the duration of the crossing
  if(dist1 < min_distance1 && record){
    min_distance1=dist1;
  }

  //If PIR is not triggered, but Ultrasonic has been, check to see if PIR gets triggered
  //PIR must also trigger to count
  if (dir==0 && record && pirStatus){
    pTrig=1;
    Serial.println("PIR Sensor triggered");
  }

  //Logic ensuring that both sensors have to be triggered to log a value
  if(uTrig > 0 && pTrig > 0 && record && millis() - tDelay > tWindow){
    //Measure height of person
    height = (d_to_floor_1 - min_distance1);
    //If height above a threshold, count adult not child
    if (height > 150){
      if (dir == 0){
        if(adults>0){
          adults--;
        }
        if(roomcount>0){
          roomcount--;
        }
        
      }
      else{
        adults++;
        roomcount++;
      }
    }
    else{
      if (dir == 0){
        if(children>0){
          children--;
        }
        if(roomcount>0){
          roomcount--;
        }
      }
      else{
        children++;
        roomcount++;
      }
    }

    //Reset loop values
    min_distance1 = 2000;
    record=false;
    uTrig=0;
    pTrig=0;
    
    //Send Height, # of Adults, # of Children, Device ID, and Flag
    //JSON format
    String str1 = "{\"height\":" + String(height/100) + ",";
    String str2 = "\"flag\":" + String(dir) + ",";
    String str3 = "\"count\":" + String(roomcount) + ",";
    String str4 = "\"adults\":" + String(adults) + ",";
    String str5 = "\"children\":" + String(children) + ",";
    String str6 = "\"deviceid\":" + String(10) + "}";
    
    String load = str1+str2+str3+str4+str5+str6;
    load.toCharArray(msgPayload, 100);
    
    mqttClient.publish(topic, msgPayload);

    Serial.println(msgPayload);
    //pirStatus = 0;
    delay(100);
    }
    //If one of the sensors is triggered, but the other isnt
    //after a time window, reset loop variables
    else if (record && (uTrig<1 || pTrig<1) && millis() - tDelay > (tWindow)){
      Serial.println("One of sensors didnt trigger");
      record=false;
      min_distance1 = d_to_floor_1;

      uTrig=0;
      pTrig=0;
      //pirStatus = 0;
    }

  //Debugging prints
  Serial.print("Distance 1:");
  Serial.println(dist1);
  Serial.print("PIR Status: ");
  Serial.println(pirStatus);
  
  Serial.print("Room Count :");
  Serial.println(roomcount);

  //Activate red count led to indicate room is full    
  if(roomcount > roomlimit){
    digitalWrite(countLED,HIGH);
  }
  else{
    digitalWrite(countLED,LOW);
  }
  
  //delay 10 ms
  delay(10);
  
  
}

void wifiCheck(){
  if (WiFi.status() != WL_CONNECTED){
    digitalWrite(mqttLED,LOW);
    Serial.println("WiFi Disconnected!");
    Serial.println("Attempting to reconnect..");
    delay(1000);
    wifiConnect();
    mqttConnect();
  }
}

void wifiConnect(){
  /*Initialize WiFi module */
  WiFi.init(&Serial1);
  /* check for the presence of ESP8266, and continue to check until detected */
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true);
  }

  /*attempt to connect to WiFi network if not already connected */
  if ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    WiFi.begin(ssid, pass);
  }
  /*Delay until module connects to the network*/
  while (WiFi.status() !=WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("You're connected to the network");
  Serial.println();
}

void mqttConnect(){
  //Set MQTT Server
  mqttClient.setServer(mqttServer,mqttPort);
  mqttClient.setCallback(callback);
  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(mqttServer);

  //Keep looping until client is connected

  while (!mqttClient.connected()) {
    digitalWrite(mqttLED,LOW);
    if (mqttClient.connect(clientID, username, password)) {
      Serial.println("connected");  
    } 
    else {
      Serial.print("failed with state ");
      Serial.print(mqttClient.state());
      delay(2000);
    }
  }
  digitalWrite(mqttLED,HIGH);
}


//Buffer for subscribing with MQTT
//Receive messages about maxroom count
void callback(char* topic, byte* payload, unsigned int length) {
  maxroomcount = roomlimit.toInt();
  Serial.print("Payload received : ");
  Serial.print(maxroomcount);
  Serial.println();
}

float calibrateDistance(int epin, int tpin){
  delay(500);
  long t = millis();
  float total = 0;
  int i=0;
  while(millis()-t <1000){
    i++;
    float measure1 = ultraSonic(epin,tpin);
    total = total+measure1;
  }
  return(total/i);
}

float ultraSonic(int epin, int tpin){
  long duration; // variable for the duration of sound wave travel
  int distance; // variable for the distance measurement
  // Clears the trigPin condition
  digitalWrite(tpin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(tpin, HIGH);
  delayMicroseconds(10);
  digitalWrite(tpin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(epin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)

  return(distance);
}
