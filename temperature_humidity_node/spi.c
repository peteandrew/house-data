#include <avr/io.h>
#include <util/delay.h>

#include "spi.h"


/* SPI port and pin definitions */
#define  OUT_REG        PORTA   // port output register
#define  IN_REG         PINA    // port input register
#define  DIR_REG        DDRA    // port direction register
#define  CLOCK_PIN      PINA2   // clock I/O pin
#define  DATAIN_PIN     PINA4   // data input pin
#define  DATAOUT_PIN    PINA3   // data output pin


void spi_init(void)
{
    // set up clock (CLK) and data out (MOSI) as output pins
    DIR_REG |= (1 << DATAOUT_PIN) | (1 << CLOCK_PIN);
    // set up data in (MISO) as input
    DIR_REG &= ~(1 << DATAIN_PIN);
    // set clock and data out low
    OUT_REG &= ~(1 << DATAOUT_PIN | 1 << CLOCK_PIN);
}


unsigned char spi_send_byte(unsigned char data)
{
    unsigned char i;
    unsigned char received = 0;

    for (i = 0; i < 8; i++)
    {
        if (data & 0x80)
        {
            OUT_REG |= (1 << DATAOUT_PIN);
        }
        else
        {
            OUT_REG &= ~(1 << DATAOUT_PIN);
        }

        _delay_us(1);

        // set clock high
        OUT_REG |= (1 << CLOCK_PIN);
        _delay_us(1);

        received <<= 1;

        if (IN_REG & (1 << DATAIN_PIN))
        {
            received |= 1;
        }
        else
        {
            received &= ~1;
        }

        // set clock low
        OUT_REG &= ~(1 << CLOCK_PIN);
        _delay_us(1);

        data <<= 1;
    }

    OUT_REG &= ~(1 << DATAOUT_PIN);

    return received;
}
