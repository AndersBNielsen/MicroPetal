#include "board.h"
#include <errno.h>
const BoardPin boardPins[NUM_DIGITAL_PINS]={
 {GPIOB,1<<0},{GPIOB,1<<1},{GPIOB,1<<2},{GPIOB,1<<3},{GPIOB,1<<4},{GPIOB,1<<5},{GPIOB,1<<6},{GPIOB,1<<7},
 {GPIOB,1<<8},{GPIOB,1<<9},{GPIOB,1<<12},{GPIOB,1<<15},{GPIOB,1<<14},{GPIOB,1<<13},
 {GPIOA,1<<0},{GPIOA,1<<1},{GPIOA,1<<2},{GPIOA,1<<3},{GPIOA,1<<4},{GPIOA,1<<5},{GPIOA,1<<6},{GPIOA,1<<7},
 {GPIOB,1<<11},{GPIOB,1<<10}};
static int readBits=10,writeBits=8;
static void detachOutput(uint8_t p);
static voidFuncPtr callbacks[16]={};
static voidFuncPtrParam paramCallbacks[16]={};
static void* callbackParams[16]={};
static uint8_t interruptOwner[16];
static uint8_t lineOf(uint16_t mask){return __builtin_ctz(mask);}
void boardAlternate(uint8_t p,uint8_t af,uint32_t mode,uint32_t pull){
 if(p>=NUM_DIGITAL_PINS)return;GPIO_InitTypeDef g={};g.Pin=boardPins[p].mask;g.Mode=mode;g.Pull=pull;g.Speed=GPIO_SPEED_FREQ_HIGH;g.Alternate=af;HAL_GPIO_Init(boardPins[p].port,&g);
}
void pinMode(pin_size_t p,PinMode m){
 if(p>=NUM_DIGITAL_PINS)return;detachOutput(p);GPIO_InitTypeDef g={};g.Pin=boardPins[p].mask;g.Speed=GPIO_SPEED_FREQ_HIGH;
 g.Mode=m==OUTPUT?GPIO_MODE_OUTPUT_PP:m==OUTPUT_OPENDRAIN?GPIO_MODE_OUTPUT_OD:GPIO_MODE_INPUT;
 g.Pull=m==INPUT_PULLUP?GPIO_PULLUP:m==INPUT_PULLDOWN?GPIO_PULLDOWN:GPIO_NOPULL;HAL_GPIO_Init(boardPins[p].port,&g);
}
void digitalWrite(pin_size_t p,PinStatus value){if(p<NUM_DIGITAL_PINS){detachOutput(p);HAL_GPIO_WritePin(boardPins[p].port,boardPins[p].mask,value==LOW?GPIO_PIN_RESET:GPIO_PIN_SET);}}
PinStatus digitalRead(pin_size_t p){return p<NUM_DIGITAL_PINS&&HAL_GPIO_ReadPin(boardPins[p].port,boardPins[p].mask)?HIGH:LOW;}
void yield(){}
unsigned long millis(){return HAL_GetTick();}
unsigned long micros(){uint32_t m1,m2,t;do{m1=millis();t=SysTick->VAL;m2=millis();}while(m1!=m2);if((SCB->ICSR&SCB_ICSR_PENDSTSET_Msk)&&t>0)m1++;return m1*1000+(SysTick->LOAD+1-t)/(SystemCoreClock/1000000);}
void delay(unsigned long ms){uint32_t t=millis();while((uint32_t)(millis()-t)<ms)yield();}
void delayMicroseconds(unsigned int us){uint32_t t=micros();while((uint32_t)(micros()-t)<us){} }
unsigned long pulseIn(pin_size_t p,uint8_t state,unsigned long timeout){uint32_t t=micros();auto expired=[&](){return (uint32_t)(micros()-t)>=timeout;};while(digitalRead(p)==state)if(expired())return 0;while(digitalRead(p)!=state)if(expired())return 0;uint32_t start=micros();while(digitalRead(p)==state)if(expired())return 0;return micros()-start;}
unsigned long pulseInLong(pin_size_t p,uint8_t state,unsigned long timeout){return pulseIn(p,state,timeout);}
void shiftOut(pin_size_t d,pin_size_t c,BitOrder order,uint8_t v){for(int i=0;i<8;i++){digitalWrite(d,(v&(1<<(order==LSBFIRST?i:7-i)))?HIGH:LOW);digitalWrite(c,HIGH);digitalWrite(c,LOW);}}
uint8_t shiftIn(pin_size_t d,pin_size_t c,BitOrder order){uint8_t v=0;for(int i=0;i<8;i++){digitalWrite(c,HIGH);if(digitalRead(d))v|=1<<(order==LSBFIRST?i:7-i);digitalWrite(c,LOW);}return v;}
void analogReadResolution(int b){if(b>=1&&b<=16)readBits=b;}
void analogWriteResolution(int b){if(b>=1&&b<=12)writeBits=b;}
void analogReference(uint8_t mode){(void)mode;} // DEFAULT: VCCA; no external AREF pin.
int analogRead(pin_size_t p){
 if(p<8)p+=14;if(p<14||p>21)return 0;
 GPIO_InitTypeDef g={};g.Pin=boardPins[p].mask;g.Mode=GPIO_MODE_ANALOG;HAL_GPIO_Init(GPIOA,&g);
 __HAL_RCC_ADC_CLK_ENABLE();ADC_HandleTypeDef h={};h.Instance=ADC1;
 __HAL_RCC_ADC_CONFIG(RCC_ADCCLKSOURCE_PCLK_DIV4);h.Init.Resolution=ADC_RESOLUTION_12B;h.Init.DataAlign=ADC_DATAALIGN_RIGHT;h.Init.ScanConvMode=ADC_SCAN_DISABLE;h.Init.ContinuousConvMode=DISABLE;h.Init.NbrOfConversion=1;h.Init.ExternalTrigConv=ADC_SOFTWARE_START;
 if(HAL_ADC_Init(&h)!=HAL_OK)return 0;HAL_ADCEx_Calibration_Start(&h);
 ADC_ChannelConfTypeDef ch={};ch.Channel=p-14;ch.Rank=1;ch.SamplingTime=ADC_SAMPLETIME_239CYCLES_5;
 HAL_ADC_ConfigChannel(&h,&ch);HAL_ADC_Start(&h);int value=0;if(HAL_ADC_PollForConversion(&h,20)==HAL_OK)value=HAL_ADC_GetValue(&h);HAL_ADC_Stop(&h);
 return readBits>12?value<<(readBits-12):value>>(12-readBits);
}
// Independent timer/channel entries: D3-D7, D9, D11. DAC is A4/A5.
struct PwmPin{uint8_t pin;TIM_TypeDef* timer;uint32_t channel;uint8_t af;};
static const PwmPin pwmPins[]={{3,TIM2,TIM_CHANNEL_2,2},{4,TIM3,TIM_CHANNEL_1,1},{5,TIM3,TIM_CHANNEL_2,1},{6,TIM1,TIM_CHANNEL_3,11},{7,TIM1,TIM_CHANNEL_1,11},{9,TIM17,TIM_CHANNEL_1,2},{11,TIM15,TIM_CHANNEL_2,1}};
static void detachOutput(uint8_t p){
 bool wasActive=false;
 for(auto &entry:pwmPins)if(entry.pin==p){uint32_t enable=TIM_CCER_CC1E<<entry.channel;wasActive=(entry.timer->CCER&enable)!=0;entry.timer->CCER&=~enable;}
 if(p==A4){wasActive=(DAC1->CR&DAC_CR_EN1)!=0;DAC1->CR&=~DAC_CR_EN1;}
 if(p==A5){wasActive=(DAC1->CR&DAC_CR_EN2)!=0;DAC1->CR&=~DAC_CR_EN2;}
 if(wasActive){GPIO_InitTypeDef g={};g.Pin=boardPins[p].mask;g.Mode=GPIO_MODE_OUTPUT_PP;g.Speed=GPIO_SPEED_FREQ_HIGH;HAL_GPIO_Init(boardPins[p].port,&g);}
}
void analogWrite(pin_size_t p,int value){
 uint32_t top=(1UL<<writeBits)-1;value=constrain(value,0,(int)top);
 if(p==A4||p==A5){__HAL_RCC_DAC1_CLK_ENABLE();GPIO_InitTypeDef g={};g.Pin=boardPins[p].mask;g.Mode=GPIO_MODE_ANALOG;HAL_GPIO_Init(GPIOA,&g);DAC_HandleTypeDef h={};h.Instance=DAC1;HAL_DAC_Init(&h);DAC_ChannelConfTypeDef c={};c.DAC_Trigger=DAC_TRIGGER_NONE;c.DAC_OutputBuffer=DAC_OUTPUTBUFFER_ENABLE;uint32_t channel=p==A4?DAC_CHANNEL_1:DAC_CHANNEL_2;HAL_DAC_ConfigChannel(&h,&c,channel);HAL_DAC_SetValue(&h,channel,DAC_ALIGN_12B_R,(uint32_t)value*4095/top);HAL_DAC_Start(&h,channel);return;}
 for(auto &entry:pwmPins)if(entry.pin==p){
 __HAL_RCC_TIM1_CLK_ENABLE();__HAL_RCC_TIM2_CLK_ENABLE();__HAL_RCC_TIM3_CLK_ENABLE();__HAL_RCC_TIM15_CLK_ENABLE();__HAL_RCC_TIM17_CLK_ENABLE();
 boardAlternate(p,entry.af);TIM_HandleTypeDef h={};h.Instance=entry.timer;h.Init.Prescaler=SystemCoreClock/1000000-1;h.Init.CounterMode=TIM_COUNTERMODE_UP;h.Init.Period=999;h.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
 // Don't reinitialize a timer already running: preserve its other PWM channel.
 if(!(entry.timer->CR1&TIM_CR1_CEN))HAL_TIM_PWM_Init(&h);else h.State=HAL_TIM_STATE_READY;
 TIM_OC_InitTypeDef c={};c.OCMode=TIM_OCMODE_PWM1;c.Pulse=(uint32_t)value*1000/top;c.OCPolarity=TIM_OCPOLARITY_HIGH;c.OCNPolarity=TIM_OCNPOLARITY_HIGH;HAL_TIM_PWM_ConfigChannel(&h,&c,entry.channel);HAL_TIM_PWM_Start(&h,entry.channel);return;}
 pinMode(p,OUTPUT);digitalWrite(p,value>(int)(top/2)?HIGH:LOW);
}
void detachInterrupt(pin_size_t p){if(p>=NUM_DIGITAL_PINS)return;uint8_t line=lineOf(boardPins[p].mask);if(interruptOwner[line]!=p)return;EXTI->IMR&=~boardPins[p].mask;callbacks[line]=nullptr;paramCallbacks[line]=nullptr;}
void attachInterrupt(pin_size_t p,voidFuncPtr f,PinStatus mode){
 if(p>=NUM_DIGITAL_PINS)return;uint8_t line=lineOf(boardPins[p].mask);callbacks[line]=f;paramCallbacks[line]=nullptr;interruptOwner[line]=p;
 GPIO_InitTypeDef g={};g.Pin=boardPins[p].mask;g.Mode=mode==RISING?GPIO_MODE_IT_RISING:mode==FALLING?GPIO_MODE_IT_FALLING:GPIO_MODE_IT_RISING_FALLING;g.Pull=GPIO_NOPULL;HAL_GPIO_Init(boardPins[p].port,&g);
 IRQn_Type irq=line<2?EXTI0_1_IRQn:line<4?EXTI2_3_IRQn:EXTI4_15_IRQn;HAL_NVIC_SetPriority(irq,2,0);HAL_NVIC_EnableIRQ(irq);
}
void attachInterruptParam(pin_size_t p,voidFuncPtrParam f,PinStatus m,void* arg){attachInterrupt(p,nullptr,m);if(p<NUM_DIGITAL_PINS){int l=lineOf(boardPins[p].mask);callbackParams[l]=arg;paramCallbacks[l]=f;}}
extern "C" void HAL_GPIO_EXTI_Callback(uint16_t mask){int line=lineOf(mask);if(callbacks[line])callbacks[line]();if(paramCallbacks[line])paramCallbacks[line](callbackParams[line]);}
extern "C" void EXTI0_1_IRQHandler(){HAL_GPIO_EXTI_IRQHandler(1);HAL_GPIO_EXTI_IRQHandler(2);}
extern "C" void EXTI2_3_IRQHandler(){HAL_GPIO_EXTI_IRQHandler(4);HAL_GPIO_EXTI_IRQHandler(8);}
extern "C" void EXTI4_15_IRQHandler(){for(int i=4;i<16;i++)HAL_GPIO_EXTI_IRQHandler(1<<i);}
extern "C" void SysTick_Handler(){HAL_IncTick();}
void init(){HAL_Init();SystemCoreClockUpdate();HAL_SYSTICK_Config(SystemCoreClock/1000);__HAL_RCC_GPIOA_CLK_ENABLE();__HAL_RCC_GPIOB_CLK_ENABLE();__HAL_RCC_GPIOC_CLK_ENABLE();__HAL_RCC_SYSCFG_CLK_ENABLE();digitalWrite(LED_BUILTIN,LED_OFF);pinMode(LED_BUILTIN,OUTPUT);}
void initVariant(){}
int main(){init();initVariant();setup();for(;;){loop();yield();}}
extern "C" void* _sbrk(ptrdiff_t n){extern char end;static char* heap=&end;char* old=heap;if(heap+n>(char*)__get_MSP()-1024 || heap+n<&end){errno=ENOMEM;return (void*)-1;}heap+=n;return old;}

extern "C" void _init(){}
extern "C" void _fini(){}
static volatile int tonePin=-1;static volatile uint32_t toneEnd=0;static volatile bool toneFinite=false,toneLevel=false;
void noTone(uint8_t p){if(tonePin==p){TIM14->CR1=0;HAL_NVIC_DisableIRQ(TIM14_IRQn);tonePin=-1;digitalWrite(p,LOW);}}
void tone(uint8_t p,unsigned int frequency,unsigned long duration){
 if(p>=NUM_DIGITAL_PINS||!frequency)return;if(tonePin>=0)noTone(tonePin);frequency=constrain(frequency,8U,20000U);pinMode(p,OUTPUT);tonePin=p;toneFinite=duration!=0;toneEnd=millis()+duration;toneLevel=false;
 __HAL_RCC_TIM14_CLK_ENABLE();TIM_HandleTypeDef h={};h.Instance=TIM14;h.Init.Prescaler=SystemCoreClock/1000000-1;h.Init.CounterMode=TIM_COUNTERMODE_UP;h.Init.Period=1000000/(2*frequency)-1;HAL_TIM_Base_Init(&h);HAL_NVIC_SetPriority(TIM14_IRQn,2,0);HAL_NVIC_EnableIRQ(TIM14_IRQn);HAL_TIM_Base_Start_IT(&h);
}
extern "C" void TIM14_IRQHandler(){if(TIM14->SR&TIM_SR_UIF){TIM14->SR=~TIM_SR_UIF;if(tonePin<0)return;if(toneFinite&&(int32_t)(millis()-toneEnd)>=0){noTone(tonePin);return;}toneLevel=!toneLevel;digitalWrite(tonePin,toneLevel?HIGH:LOW);}}

extern "C" {
#include <sys/stat.h>
#include <errno.h>
#include <stdint.h>
int _write(int fd,char *data,int len){(void)fd;(void)data;(void)len;errno=ENOSYS;return -1;}
int _read(int fd,char *data,int len){(void)fd;(void)data;(void)len;errno=ENOSYS;return -1;}
int _close(int fd){(void)fd;errno=EBADF;return -1;}
int _fstat(int fd,struct stat *st){(void)fd;st->st_mode=S_IFCHR;return 0;}
int _isatty(int fd){return fd>=0 && fd<=2;}
int _lseek(int fd,int offset,int whence){(void)fd;(void)offset;(void)whence;errno=ESPIPE;return -1;}
int _getpid(void){return 1;}
int _kill(int pid,int sig){(void)pid;(void)sig;errno=EINVAL;return -1;}
void _exit(int status){(void)status;while(1){} }

}
long random(long max){return max>0?rand()%max:0;}
long random(long min,long max){return min<max?min+random(max-min):min;}
void randomSeed(unsigned long seed){if(seed)srand(seed);}
