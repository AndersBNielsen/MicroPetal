// External LED: D3 -> 1k resistor -> LED anode; LED cathode -> GND.
// Built-in D13 LED is not on a supported ordinary PWM channel.
void setup() {}
void loop() { for(int v=0;v<256;v++){analogWrite(3,v);delay(5);} for(int v=255;v>=0;v--){analogWrite(3,v);delay(5);} }
