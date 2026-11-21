#pragma once
#define NUM_DIGITAL_PINS 24
#define NUM_ANALOG_INPUTS 8
#define LED_BUILTIN 13
#define LED_ON LOW
#define LED_OFF HIGH
#define BUTTON_BUILTIN 12
#define PIN_SERIAL_RX 0
#define PIN_SERIAL_TX 2
#define PIN_WIRE_SDA 22
#define PIN_WIRE_SCL 23
static const uint8_t A0=14,A1=15,A2=16,A3=17,A4=18,A5=19,A6=20,A7=21;
static const uint8_t SDA=22,SCL=23,SS=10,MOSI=11,MISO=12,SCK=13;
#define digitalPinToInterrupt(p) (p)
#define digitalPinHasPWM(p) ((p)==3 || (p)==4 || (p)==5 || (p)==6 || (p)==7 || (p)==9 || (p)==11)
