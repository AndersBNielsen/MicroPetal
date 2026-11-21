#pragma once
#include "api/HardwareSerial.h"
class MicroPetalSerial : public arduino::HardwareSerial {
 UART_HandleTypeDef uart={}; uint8_t buffer[128]; volatile uint8_t head=0,tail=0; int cached=-1; bool active=false;
public:
 void begin(unsigned long baud) override { begin(baud,SERIAL_8N1); }
 void begin(unsigned long,uint16_t) override;
 void end() override;
 int available() override;
 int peek() override;
 int read() override;
 void flush() override;
 size_t write(uint8_t) override;
 using arduino::Print::write;
 size_t write(int b){return write((uint8_t)b);}
 size_t write(unsigned int b){return write((uint8_t)b);}
 size_t write(long b){return write((uint8_t)b);}
 size_t write(unsigned long b){return write((uint8_t)b);}
 operator bool() override {return active;}
 void irq();
};
extern MicroPetalSerial Serial;
#define Serial1 Serial
