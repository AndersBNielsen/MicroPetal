// MicroPetal glue, MIT. Pull in nano printf floating point only when this object is linked.
#include <stdio.h>
__asm__(".global _printf_float");
char *dtostrf(double value,signed char width,unsigned char precision,char *out){
 // Matches the AVR API: the caller must provide sufficient output storage.
 sprintf(out,"%*.*f",(int)width,(int)precision,value);
 return out;
}
