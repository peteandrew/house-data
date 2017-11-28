#include <util/delay.h>
#include <avr/io.h>

#include "temp.h"

uint8_t therm_reset()
{

	uint8_t i;

	//Pull line low and wait for 480uS
	THERM_LOW();
	THERM_OUTPUT_MODE();
	_delay_us(480);

	//Release line and wait for 60uS
	THERM_INPUT_MODE();
	_delay_us(60);

	//Store line value and wait until the completion of 480uS period
	i=(THERM_PIN & (1<<THERM_DQ));
	_delay_us(480);

	//Return the value read from the presence pulse (0=OK, 1=WRONG)
	return i;
}

void therm_write_bit(uint8_t bit)
{

	//Pull line low for 1uS
	THERM_LOW();
	THERM_OUTPUT_MODE();
	_delay_us(1);

	//If we want to write 1, release the line (if not will keep low)
	if(bit) THERM_INPUT_MODE();

	//Wait for 60uS and release the line
	_delay_us(60);
	THERM_INPUT_MODE();
}

uint8_t therm_read_bit(void)
{

	uint8_t bit=0;

	//Pull line low for 1uS
	THERM_LOW();
	THERM_OUTPUT_MODE();
	_delay_us(1);

	//Release line and wait for 14uS
	THERM_INPUT_MODE();
	_delay_us(14);

	//Read line value
	if(THERM_PIN&(1<<THERM_DQ)) bit=1;

	//Wait for 45uS to end and return read value
	_delay_us(45);
	return bit;
}

uint8_t therm_read_byte(void)
{
	uint8_t i=8, n=0;
	while(i--)
	{
		//Shift one position right and store read value
		n>>=1;
		n|=(therm_read_bit()<<7);
	}
	return n;
}

void therm_write_byte(uint8_t byte)
{

	uint8_t i=8;

	while(i--)
	{
		//Write actual bit and shift one position right to make the next bit ready
		therm_write_bit(byte&1);
		byte>>=1;
	}
}
