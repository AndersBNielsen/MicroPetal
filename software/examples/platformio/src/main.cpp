#include <Arduino.h>
// MicroPetal's LED is active-low: LOW turns it on.
void setup() { pinMode(LED_BUILTIN, OUTPUT); }
void loop() {
  digitalWrite(LED_BUILTIN, LED_ON); delay(500);
  digitalWrite(LED_BUILTIN, LED_OFF); delay(500);
}
