// Jumper D11 MOSI to D12 MISO. Do not press BTN during this test.
#include <SPI.h>
void setup() { Serial.begin(115200);SPI.begin(); }
void loop() {
 SPI.beginTransaction(SPISettings(100000,MSBFIRST,SPI_MODE0));
 digitalWrite(SS,LOW);uint8_t result=SPI.transfer((uint8_t)0xA5);digitalWrite(SS,HIGH);
 SPI.endTransaction();Serial.println(result==0xA5?"PASS":"FAIL");delay(1000);
}
