#include "Wire.h"
TwoWire Wire;
void TwoWire::begin(){digitalWrite(SDA,HIGH);digitalWrite(SCL,HIGH);pinMode(SDA,OUTPUT_OPENDRAIN);pinMode(SCL,OUTPUT_OPENDRAIN);held=false;}
void TwoWire::end(){stop();pinMode(SDA,INPUT);pinMode(SCL,INPUT);}
void TwoWire::setClock(uint32_t hz){hz=constrain(hz,1000UL,100000UL);halfPeriod=(500000+hz-1)/hz;}
bool TwoWire::clockHigh(){digitalWrite(SCL,HIGH);uint32_t t=micros();while(digitalRead(SCL)==LOW)if((uint32_t)(micros()-t)>25000)return false;delayMicroseconds(halfPeriod);return true;}
bool TwoWire::start(){digitalWrite(SDA,HIGH);delayMicroseconds(halfPeriod);if(!clockHigh())return false;if(digitalRead(SDA)==LOW)return false;digitalWrite(SDA,LOW);delayMicroseconds(halfPeriod);digitalWrite(SCL,LOW);held=true;return true;}
void TwoWire::stop(){digitalWrite(SCL,LOW);digitalWrite(SDA,LOW);delayMicroseconds(halfPeriod);clockHigh();digitalWrite(SDA,HIGH);delayMicroseconds(halfPeriod);held=false;}
bool TwoWire::send(uint8_t b){for(int i=0;i<8;i++){digitalWrite(SDA,b&128?HIGH:LOW);b<<=1;delayMicroseconds(halfPeriod);if(!clockHigh())return false;digitalWrite(SCL,LOW);}digitalWrite(SDA,HIGH);delayMicroseconds(halfPeriod);if(!clockHigh())return false;bool ack=digitalRead(SDA)==LOW;digitalWrite(SCL,LOW);return ack;}
bool TwoWire::receive(uint8_t& b,bool ack){b=0;digitalWrite(SDA,HIGH);for(int i=0;i<8;i++){delayMicroseconds(halfPeriod);if(!clockHigh())return false;b=(b<<1)|digitalRead(SDA);digitalWrite(SCL,LOW);}digitalWrite(SDA,ack?LOW:HIGH);delayMicroseconds(halfPeriod);if(!clockHigh())return false;digitalWrite(SCL,LOW);digitalWrite(SDA,HIGH);return true;}
uint8_t TwoWire::endTransmission(bool sendStop){if(overflow){if(held)stop();return 1;}if(!start()){stop();return 4;}if(!send(address<<1)){stop();return 2;}for(int i=0;i<txlen;i++)if(!send(tx[i])){stop();return 3;}if(sendStop)stop();return 0;}
size_t TwoWire::requestFrom(uint8_t a,size_t n,bool sendStop){rxlen=index=0;n=min(n,(size_t)32);if(!start()||!send((a<<1)|1)){stop();return 0;}while(rxlen<n){uint8_t b;if(!receive(b,rxlen+1<n)){stop();return rxlen;}rx[rxlen++]=b;}if(sendStop)stop();return rxlen;}
