#pragma once
#include "py32f07x_hal.h"
#include "api/ArduinoAPI.h"
#include "pins_arduino.h"
#define interrupts() __enable_irq()
#define noInterrupts() __disable_irq()
#define DEFAULT 0
#ifdef __cplusplus
using namespace arduino;
inline void digitalWrite(pin_size_t p,int value){digitalWrite(p,value?HIGH:LOW);}
inline void pinMode(pin_size_t p,int mode){pinMode(p,(PinMode)mode);}
#include "HardwareSerial.h"
void analogReadResolution(int bits);
void analogWriteResolution(int bits);

void noTone(uint8_t pin);
#endif
