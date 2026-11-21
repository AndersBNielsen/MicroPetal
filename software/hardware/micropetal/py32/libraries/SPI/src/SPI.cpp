#include "SPI.h"
#include "board.h"
MicroPetalSPI SPI;
void MicroPetalSPI::begin(){__HAL_RCC_SPI2_CLK_ENABLE();digitalWrite(SS,HIGH);pinMode(SS,OUTPUT);boardAlternate(SCK,0);boardAlternate(MOSI,0);boardAlternate(MISO,0);h.Instance=SPI2;beginTransaction(SPISettings());endTransaction();}
void MicroPetalSPI::end(){HAL_SPI_DeInit(&h);active=false;pinMode(SCK,INPUT);pinMode(MOSI,INPUT);pinMode(MISO,INPUT);}
void MicroPetalSPI::beginTransaction(SPISettings settings){
 if(maskInterrupts){savedPrimask=__get_PRIMASK();__disable_irq();}
 lsb=settings.getBitOrder()==LSBFIRST;h.Init.Mode=SPI_MODE_MASTER;h.Init.Direction=SPI_DIRECTION_2LINES;h.Init.DataSize=SPI_DATASIZE_8BIT;h.Init.NSS=SPI_NSS_SOFT;
 h.Init.CLKPolarity=(settings.getDataMode()==arduino::SPI_MODE2||settings.getDataMode()==arduino::SPI_MODE3)?SPI_POLARITY_HIGH:SPI_POLARITY_LOW;
 h.Init.CLKPhase=(settings.getDataMode()==arduino::SPI_MODE1||settings.getDataMode()==arduino::SPI_MODE3)?SPI_PHASE_2EDGE:SPI_PHASE_1EDGE;
 const uint32_t prescalers[]={SPI_BAUDRATEPRESCALER_2,SPI_BAUDRATEPRESCALER_4,SPI_BAUDRATEPRESCALER_8,SPI_BAUDRATEPRESCALER_16,SPI_BAUDRATEPRESCALER_32,SPI_BAUDRATEPRESCALER_64,SPI_BAUDRATEPRESCALER_128,SPI_BAUDRATEPRESCALER_256};
 int i=0;while(i<7&&SystemCoreClock/(2U<<i)>settings.getClockFreq())i++;h.Init.BaudRatePrescaler=prescalers[i];h.Init.FirstBit=lsb?SPI_FIRSTBIT_LSB:SPI_FIRSTBIT_MSB;h.Init.CRCCalculation=SPI_CRCCALCULATION_DISABLE;h.Init.CRCPolynomial=7;
 active=HAL_SPI_Init(&h)==HAL_OK;
}
void MicroPetalSPI::endTransaction(){if(maskInterrupts)__set_PRIMASK(savedPrimask);}
uint8_t MicroPetalSPI::transfer(uint8_t b){uint8_t r=0; // Bounded polling avoids a SysTick-dependent timeout with interrupts masked.
 if(!active)return 0;__HAL_SPI_ENABLE(&h);uint32_t count=100000;while(!(SPI2->SR&SPI_SR_TXE)&&--count){}if(!count)return 0;*(__IO uint8_t*)&SPI2->DR=b;count=100000;while(!(SPI2->SR&SPI_SR_RXNE)&&--count){}if(count)r=*(__IO uint8_t*)&SPI2->DR;return r;}
uint16_t MicroPetalSPI::transfer16(uint16_t b){uint8_t first=transfer(lsb?b:b>>8),second=transfer(lsb?b>>8:b);return lsb?(second<<8)|first:(first<<8)|second;}
void MicroPetalSPI::transfer(void* buf,size_t n){uint8_t* b=(uint8_t*)buf;while(n--){*b=transfer(*b);b++;}}
