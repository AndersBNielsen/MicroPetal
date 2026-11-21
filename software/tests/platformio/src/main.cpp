#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
void edge(){}
void setup() {
 pinMode(LED_BUILTIN,OUTPUT);pinMode(BUTTON_BUILTIN,INPUT_PULLUP);
 Serial.begin(115200);Serial.println("MicroPetal smoke test");String s="Value=";s+=analogRead(A0);Serial.println(s);Serial.println(3.14); String f=String(1.234,2);Serial.println(f);Serial.println(random(10));
 analogReadResolution(12);analogWriteResolution(8);analogWrite(3,128);analogWrite(A4,128);
 Wire.begin();Wire.beginTransmission(0x50);Wire.write(0);Wire.endTransmission(false);Wire.requestFrom((uint8_t)0x50,(size_t)1);Wire.end();
 SPI.begin();SPI.beginTransaction(SPISettings(1000000,MSBFIRST,SPI_MODE0));SPI.transfer((uint8_t)0);SPI.endTransaction();SPI.end();
 attachInterrupt(digitalPinToInterrupt(4),edge,RISING);detachInterrupt(4);tone(5,440,50);
}
void loop() { digitalWrite(LED_BUILTIN,LED_ON);delay(500);digitalWrite(LED_BUILTIN,LED_OFF);delay(500); }
