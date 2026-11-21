#include "board.h"
MicroPetalSerial Serial;
void MicroPetalSerial::begin(unsigned long baud,uint16_t config) {
 end(); if(config!=SERIAL_8N1) return; // Explicitly unsupported formats do not silently become 8N1.
 __HAL_RCC_USART3_CLK_ENABLE(); boardAlternate(PIN_SERIAL_TX,10);boardAlternate(PIN_SERIAL_RX,10,GPIO_MODE_AF_PP,GPIO_PULLUP);
 uart.Instance=USART3;uart.Init.BaudRate=baud;uart.Init.WordLength=UART_WORDLENGTH_8B;uart.Init.StopBits=UART_STOPBITS_1;uart.Init.Parity=UART_PARITY_NONE;uart.Init.Mode=UART_MODE_TX_RX;uart.Init.HwFlowCtl=UART_HWCONTROL_NONE;uart.Init.OverSampling=UART_OVERSAMPLING_16;
 active=HAL_UART_Init(&uart)==HAL_OK;head=tail=0;cached=-1;
 if(active){ __HAL_UART_ENABLE_IT(&uart,UART_IT_RXNE);HAL_NVIC_SetPriority(USART3_4_IRQn,2,0);HAL_NVIC_EnableIRQ(USART3_4_IRQn); }
}
void MicroPetalSerial::end(){if(active){HAL_NVIC_DisableIRQ(USART3_4_IRQn);HAL_UART_DeInit(&uart);}active=false;}
int MicroPetalSerial::available(){return (uint8_t)((head-tail)&127);}
int MicroPetalSerial::peek(){return head==tail ? -1:buffer[tail];}
int MicroPetalSerial::read(){if(head==tail)return -1;int c=buffer[tail];tail=(tail+1)&127;return c;}
void MicroPetalSerial::flush(){if(active)while(!__HAL_UART_GET_FLAG(&uart,UART_FLAG_TC)){} }
size_t MicroPetalSerial::write(uint8_t c){return active&&HAL_UART_Transmit(&uart,&c,1,100)==HAL_OK?1:0;}
void MicroPetalSerial::irq(){
 if(USART3->SR & USART_SR_RXNE){uint8_t c=USART3->DR;uint8_t next=(head+1)&127;if(next!=tail){buffer[head]=c;head=next;}}
 else if(USART3->SR & (USART_SR_ORE|USART_SR_FE|USART_SR_NE)){volatile uint32_t ignored=USART3->DR;(void)ignored;}
}
extern "C" void USART3_4_IRQHandler(){Serial.irq();}
