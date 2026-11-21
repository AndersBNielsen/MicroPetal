#include <Wire.h>
void setup() { Serial.begin(115200);Wire.begin(); }
void loop() {
 Serial.println("Scanning dedicated SDA/SCL pins...");
 for(uint8_t address=1;address<127;address++) {
  Wire.beginTransmission(address);
  if(Wire.endTransmission()==0) { Serial.print("Found 0x");Serial.println(address,HEX); }
 }
 delay(3000);
}
