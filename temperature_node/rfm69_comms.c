#include <avr/io.h>
#include <util/delay.h>

#include "spi.h"
#include "rfm69_comms.h"


#define  OUT_REG    PORTB   // port output register
#define  DIR_REG    DDRB    // port direction register
#define  SS_PIN     PINB3   // Slave select pin


void rfm69_comms_init(void)
{
    spi_init();
    // set up slave select as output pin
    DIR_REG |= (1 << SS_PIN);
    // set slave select high
    OUT_REG |= (1 << SS_PIN);
}


void select(void)
{
    // set slave select low
    OUT_REG &= ~(1 << SS_PIN);

    _delay_us(1);
}


void unselect(void)
{
    _delay_us(1);

    // set slave select high
    OUT_REG |= (1 << SS_PIN);
}


unsigned char read_reg(unsigned char addr)
{
    unsigned char received = 0;

    select();

    // first bit should be 0 for read
    spi_send_byte(addr & 0x7F);
    received = spi_send_byte(0);

    unselect();

    return received;
}


void write_reg(unsigned char addr, unsigned char data)
{
    select();

    // first bit should be 1 for write
    spi_send_byte(addr | 0x80);
    spi_send_byte(data);

    unselect();
}
