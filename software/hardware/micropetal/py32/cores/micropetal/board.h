#pragma once
#include "Arduino.h"
struct BoardPin { GPIO_TypeDef *port; uint16_t mask; };
extern const BoardPin boardPins[NUM_DIGITAL_PINS];
void boardAlternate(uint8_t pin,uint8_t af,uint32_t mode=GPIO_MODE_AF_PP,uint32_t pull=GPIO_NOPULL);
