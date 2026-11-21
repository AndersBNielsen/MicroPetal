#pragma once
#include <Arduino.h>
#include <api/HardwareSPI.h>
using arduino::SPISettings;
class MicroPetalSPI {
 SPI_HandleTypeDef h={}; bool lsb=false,active=false;uint32_t savedPrimask=0;bool maskInterrupts=false;
public:
 void begin();void end();void beginTransaction(SPISettings settings);void endTransaction();
 uint8_t transfer(uint8_t b);uint16_t transfer16(uint16_t b);void transfer(void* buf,size_t count);
 void usingInterrupt(int n){(void)n;maskInterrupts=true;}void notUsingInterrupt(int n){(void)n;maskInterrupts=false;}
};
using SPIClass=MicroPetalSPI;
extern MicroPetalSPI SPI;
