void setup() { pinMode(LED_BUILTIN,OUTPUT);pinMode(BUTTON_BUILTIN,INPUT_PULLUP); }
void loop() { digitalWrite(LED_BUILTIN,digitalRead(BUTTON_BUILTIN)==LOW?LED_ON:LED_OFF); }
