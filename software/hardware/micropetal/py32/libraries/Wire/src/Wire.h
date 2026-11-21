#pragma once
#include <Arduino.h>
// Controller-only software I2C; supports repeated START and clock stretching.
class TwoWire : public arduino::Stream {
 uint8_t tx[32],rx[32],txlen=0,rxlen=0,index=0,address=0;bool overflow=false,held=false;uint32_t halfPeriod=5;
 bool clockHigh();bool start();void stop();bool send(uint8_t);bool receive(uint8_t&,bool);
public:
 void begin();void end();void setClock(uint32_t hz);
 void beginTransmission(uint8_t a){address=a;txlen=0;overflow=false;}
 uint8_t endTransmission(bool sendStop=true);
 size_t requestFrom(uint8_t a,size_t n,bool sendStop=true);
 size_t write(uint8_t b) override {if(txlen>=32){overflow=true;return 0;}tx[txlen++]=b;return 1;}
 using arduino::Print::write;
 size_t write(int b){return write((uint8_t)b);}
 size_t write(unsigned int b){return write((uint8_t)b);}
 size_t write(long b){return write((uint8_t)b);}
 size_t write(unsigned long b){return write((uint8_t)b);}
 int available() override {return rxlen-index;}
 int read() override {return index<rxlen?rx[index++]:-1;}
 int peek() override {return index<rxlen?rx[index]:-1;}
 void flush() override {}
};
extern TwoWire Wire;
